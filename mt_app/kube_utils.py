from kubernetes import client
from kubernetes.client import ApiException

api_networking_v1 = client.NetworkingV1Api()

api_apps_v1 = client.AppsV1Api()
api_core_v1 = client.CoreV1Api()

NAME_SPACE = "serverless"
INGRESS_NAME = "main-ingress"


def create_deployment(identifier, deployment_name, app_name):
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=deployment_name, labels={"app": app_name}),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(match_labels={"app": app_name}),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": app_name}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="web",
                            image="apurvchaudhary/status_page_django_app:latest",
                            command=["/app/entrypoint.sh"],
                            args=["uvicorn", "project.asgi:application", "--host", "0.0.0.0", "--port", "8000"],
                            env=[
                                client.V1EnvVar(name="DB_HOST", value="postgres"),
                                client.V1EnvVar(name="DB_SCHEMA", value=identifier),
                            ],
                            volume_mounts=[client.V1VolumeMount(name="shared-static", mount_path="/app/static")],
                        ),
                        client.V1Container(
                            name="celery",
                            image="apurvchaudhary/status_page_django_app:latest",
                            command=["/app/entrypoint.sh"],
                            args=["celery", "-A", "project", "worker", "--loglevel=info"],
                            env=[
                                client.V1EnvVar(name="DB_HOST", value="postgres"),
                                client.V1EnvVar(name="DB_SCHEMA", value=identifier),
                            ],
                        ),
                        client.V1Container(
                            name="redis", image="redis:7-alpine", ports=[client.V1ContainerPort(container_port=6379)]
                        ),
                        client.V1Container(
                            name="nginx",
                            image="nginx:alpine",
                            ports=[client.V1ContainerPort(container_port=80)],
                            volume_mounts=[
                                client.V1VolumeMount(name="shared-static", mount_path="/static"),
                                client.V1VolumeMount(
                                    name="nginx-config", mount_path="/etc/nginx/nginx.conf", sub_path="nginx.conf"
                                ),
                            ],
                        ),
                    ],
                    volumes=[
                        client.V1Volume(name="shared-static", empty_dir={}),
                        client.V1Volume(
                            name="nginx-config", config_map=client.V1ConfigMapVolumeSource(name="nginx-config-map")
                        ),
                    ],
                ),
            ),
        ),
    )
    return deployment


def create_service(service_name, app_name):
    service = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(name=service_name),
        spec=client.V1ServiceSpec(
            selector={"app": app_name}, ports=[client.V1ServicePort(protocol="TCP", port=80, target_port=80)]
        ),
    )
    return service


def add_host_to_ingress(new_host, service_name):
    new_rule = client.V1IngressRule(
        host=new_host,
        http=client.V1HTTPIngressRuleValue(
            paths=[
                client.V1HTTPIngressPath(
                    path="/",
                    path_type="Prefix",
                    backend=client.V1IngressBackend(
                        service=client.V1IngressServiceBackend(
                            name=service_name, port=client.V1ServiceBackendPort(number=80)
                        )
                    ),
                )
            ]
        ),
    )
    return new_rule


def update_ingress(new_host, service_name):
    existing_ingress = api_networking_v1.read_namespaced_ingress(name=INGRESS_NAME, namespace=NAME_SPACE)
    if existing_ingress:
        if existing_ingress.spec.rules is None:
            existing_ingress.spec.rules = []
        new_rule = add_host_to_ingress(new_host, service_name)
        existing_ingress.spec.rules.append(new_rule)
        api_networking_v1.patch_namespaced_ingress(name=INGRESS_NAME, namespace=NAME_SPACE, body=existing_ingress)
    else:
        raise ApiException("Failed to fetch existing Ingress resource.")


def deploy_pod(identifier):
    deployment_name = f"status-page-deployment-{identifier}"
    app_name = f"status-page-{identifier}"
    try:
        deployment = create_deployment(identifier, deployment_name, app_name)
        api_apps_v1.create_namespaced_deployment(namespace=NAME_SPACE, body=deployment)
        return True, f"Pod created successfully.", "pod"
    except ApiException as pod_error:
        return False, f"Error in creating pod {pod_error}", "pod"


def deploy_service(identifier):
    service_name = f"status-page-service-{identifier}"
    app_name = f"status-page-{identifier}"
    try:
        service = create_service(service_name, app_name)
        api_core_v1.create_namespaced_service(namespace=NAME_SPACE, body=service)
        return True, f"Service created successfully.", "service"
    except ApiException as service_error:
        return False, f"Error in creating service {service_error}", "service"


def deploy_ingress(identifier):
    new_host = f"{identifier}.status"
    service_name = f"status-page-service-{identifier}"
    try:
        update_ingress(new_host, service_name)
        return True, f"{new_host} added successfully.", "load_balancer"
    except ApiException as ingress_error:
        return False, f"Error in adding {new_host} {ingress_error}", "load_balancer"


def delete_pod(identifier):
    deployment_name = f"status-page-deployment-{identifier}"
    try:
        api_apps_v1.delete_namespaced_deployment(
            name=deployment_name, namespace=NAME_SPACE, body=client.V1DeleteOptions()
        )
        return True, f"Pod deleted successfully.", "pod"
    except client.exceptions.ApiException as pod_error:
        return False, f"Error in deleting deployment: {pod_error}", "pod"


def delete_service(identifier):
    service_name = f"status-page-service-{identifier}"
    try:
        api_core_v1.delete_namespaced_service(name=service_name, namespace=NAME_SPACE)
        return True, f"Service deleted successfully.", "service"
    except client.exceptions.ApiException as e:
        return False, f"Error in deleting service: {e}", "service"


def delete_from_ingress(identifier):
    host = f"{identifier}.status"
    try:
        existing_ingress = api_networking_v1.read_namespaced_ingress(name=INGRESS_NAME, namespace=NAME_SPACE)
        if existing_ingress and existing_ingress.spec.rules:
            updated_rules = [rule for rule in existing_ingress.spec.rules if rule.host != host]
            existing_ingress.spec.rules = updated_rules
            api_networking_v1.patch_namespaced_ingress(name=INGRESS_NAME, namespace=NAME_SPACE, body=existing_ingress)
            return True, f"{host} deleted successfully.", "load_balancer"
        else:
            return False, f"Failed to fetch existing Ingress resource.", "load_balancer"
    except client.exceptions.ApiException as ingress_error:
        return False, f"Error in deleting {host} {ingress_error}", "load_balancer"
