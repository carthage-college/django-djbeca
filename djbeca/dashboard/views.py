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
from djtools.utils.users import in_group


def departments(cid):
    depts = {}
    dean = False
    sql = """
        SELECT
            dept_table.dept,
            dept_table.txt as dept_txt,
            div_table.txt as div_txt
        FROM
            dept_table
        INNER JOIN
            div_table ON dept_table.div = div_table.div
        WHERE
            div_table.div not in ("NSSS")
        AND
            div_table.head_id={}
    """.format(cid)
    objs = do_esql(sql).fetchall()
    if objs:
        # division dean
        dean = True
    else:
        # department chair
        dean = False
        sql = "SELECT dept, txt as dept_txt from dept_table WHERE head_id={}".format(cid)
        objs = do_esql(sql).fetchall()
    for o in objs:
        depts[(o.dept)] = o.dept_txt
        if dean:
            dean = o.div_txt
    return {"depts":depts, "div":dean}


@portal_auth_required(
    "Chairs and Deans",
    "Chairs and Deans", reverse_lazy("access_denied")
)
def proposal_list(request):

    if in_group(request.user,"Office of Sponsored Programs"):
        proposals = Proposal.objects.all()
        depts = False
        div = False
    else:
        depts = departments(request.user.id)
        div = depts["div"]
        depts = depts["depts"]
        proposals = Proposal.objects.filter(
            department__in=[ key for key,val in depts.iteritems() ]
        )

    return render_to_response(
        "home.html",
        {
            "proposals":proposals,"home":False,
            "depts":depts,"div":div
        },
        context_instance=RequestContext(request)
    )


@portal_auth_required(
    "Chairs and Deans",
    "Chairs and Deans", reverse_lazy("access_denied")
)
def proposal_detail(request, pid):

    proposal = Proposal.objects.get(id=pid)

    return render_to_response(
        "detail.html",
        {"proposal":proposal},
        context_instance=RequestContext(request)
    )

