import json

from edunext_openedx_extensions.ednx_microsites.models import Microsite


def transform_microsites_to_stage(suffix_stage_domain=""):
    """
    This function will iterate over all microsites objects to change microsite prod domains to a stage versions.
    The domains are converted as follows:
    my.microsite.domain => my-microsite-domain-{suffix_stage_domain}

    The microsite configurations containing the value of the original domain will be replaced
    by stage domain as well
    """
    if not suffix_stage_domain:
        suffix_stage_domain = u"stage.edunext.co"

    for microsite in Microsite.objects.all():

        # Don't bother on changing anything if the suffix is correct
        if microsite.subdomain.endswith(suffix_stage_domain):
            continue

        try:
            # Transforming the domain to format my-microsite-domain-{suffix_stage_domain}
            stage_domain = "{}-{}".format(
                microsite.subdomain.replace('.', '-'),
                suffix_stage_domain
            )
        except Exception as e:
            stage_domain = ""
            message = u"Unable to define stage url for microsite {}".format(
                microsite.subdomain
            )
            print(message)
            print(u"The error is: {}".format(e.message))

        if not stage_domain:
            continue

        prod_subdomain = microsite.subdomain
        microsite.subdomain = stage_domain

        configs_string = json.dumps(microsite.values)
        # Replacing all concidences of the prod domain inside the configurations by the stage domain
        modified_configs_string = configs_string.replace(
            prod_subdomain,
            stage_domain
        )
        microsite.values = json.loads(modified_configs_string)
        microsite.save()

    return
