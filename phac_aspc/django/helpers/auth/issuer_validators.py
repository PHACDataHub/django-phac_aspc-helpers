from phac_aspc.django.settings.security_env import get_oauth_env_value


def validate_ms_iss(claims, value):
    """Validate the iss claim"""
    tenant = get_oauth_env_value("MICROSOFT_TENANT")
    use_tenant = tenant if tenant != "common" else claims["tid"]
    # iss = "https://login.microsoftonline.com/{}/v2.0".format(use_tenant)
    return use_tenant in value


def validate_dev_sg_iss(claims, value):
    return (
        value == "https://hcscb2cdev.gateway-passerelle.hc-sc.canada.ca/auth/realms/sg"
    )


ISS_VALIDATORS = {
    "microsoft": validate_ms_iss,
    "dev_secure_gateway": validate_dev_sg_iss,
}
