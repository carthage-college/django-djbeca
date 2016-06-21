from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy

from djbeca.core.models import Proposal
from djbeca.core.forms import ProposalForm

from djzbar.utils.hr import person_departments
from djzbar.utils.hr import department_divison_chairs
from djzbar.decorators.auth import portal_auth_required
from djzbar.utils.informix import do_sql as do_esql
from djtools.utils.mail import send_mail
from djtools.utils.users import in_group

import logging
logger = logging.getLogger(__name__)


def departments(cid):
    depts = []
    # check for division dean
    sql = """
        SELECT
            dept_table.dept
        FROM
            dept_table
        INNER JOIN
            div_table ON dept_table.div = div_table.div
        WHERE
            div_table.head_id={}
    """.format(cid)
    logger.debug("sql = {}".format(sql))
    objs = do_esql(sql).fetchall()
    # if not, we have a department chair:
    if not objs:
        sql = "SELECT dept from dept_table WHERE head_id={}".format(cid)
        logger.debug("sql = {}".format(sql))
        objs = do_esql(sql).fetchall()
    for o in objs:
        depts.append(o.dept)
    logger.debug("depts = {}".format(depts))
    return depts


@portal_auth_required(
    "Chairs and Deans",
    "Chairs and Deans", reverse_lazy("access_denied")
)
def proposal_list(request):

    if in_group(request.user,"Office of Sponsored Programs"):
        proposals = Proposal.objects.all()
    else:
        depts = departments(request.user.id)
        proposals = Proposal.objects.filter(department__in=depts)

    return render_to_response(
        "dashboard/home.html",
        {"proposals":proposals},
        context_instance=RequestContext(request)
    )


@portal_auth_required(
    "Chairs and Deans",
    "Chairs and Deans", reverse_lazy("access_denied")
)
def proposal_detail(request, pid):

    proposal = Proposal.objects.get(id=pid)

    return render_to_response(
        "dashboard/detail.html",
        {"proposal":proposal},
        context_instance=RequestContext(request)
    )

