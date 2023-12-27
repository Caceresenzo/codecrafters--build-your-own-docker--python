import json
import os
import sys
import urllib.request
import tarfile


def _debug(message: str):
    print(message, file=sys.stderr)


def _get(url: str, headers: dict = {}):
    request = urllib.request.Request(url, headers=headers)

    return urllib.request.urlopen(request)


def _get_json(url: str, headers: dict = {}):
    with _get(url, headers) as response:
        return json.load(response)


def _auth(image_name: str):
    content = _get_json(
        f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{image_name}:pull"
    )

    return content["token"]


def _authorization_header(access_token: str):
    return {
        "Authorization": f"Bearer {access_token}"
    }


def _list_layers_digest(image_name: str, image_label: str, access_token: str):
    content = _get_json(
        f"https://registry-1.docker.io/v2/{image_name}/manifests/{image_label}",
        headers=_authorization_header(access_token)
    )

    if "manifests" not in content:
        return [
            layer["blobSum"]
            for layer in content["fsLayers"]
        ]

    def match_arch(manifest: dict):
        platform = manifest["platform"]

        return platform["architecture"] == "amd64" and platform["os"] == "linux"

    digest = next((
        manifest["digest"]
        for manifest in content["manifests"]
        if match_arch(manifest)
    ))

    content = _get_json(
        f"https://registry-1.docker.io/v2/{image_name}/manifests/{digest}",
        headers={
            "Accept": "application/vnd.oci.image.manifest.v1+json",
            **_authorization_header(access_token),
        }
    )

    return [
        layer["digest"]
        for layer in content["layers"]
    ]


def _download_layer_digest(image_name: str, layer_digest: str, access_token: str):
    path = os.path.join("layers", image_name, layer_digest)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        _debug(f"skip {image_name} {layer_digest}")
        return path

    _debug(f"download {image_name} {layer_digest}")

    with _get(
        f"https://registry-1.docker.io/v2/{image_name}/blobs/{layer_digest}",
        headers=_authorization_header(access_token)
    ) as response:
        content = response.read()

        with open(path, "wb") as fd:
            fd.write(content)

    return path


def pull(image: str, root_path: str):
    name, label = image.split(":", 2)
    if "/" not in name:
        name = f"library/{name}"

    access_token = _auth(name)
    layers_digest = _list_layers_digest(name, label, access_token)

    for layer_digest in layers_digest:
        path = _download_layer_digest(name, layer_digest, access_token)

        with tarfile.open(path) as tar:
            tar.extractall(root_path)
