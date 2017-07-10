FUNDING_CHOICES = (
    ('Pursuit of Funding', 'Pursuit of Funding'),
    ('Funding Identified', 'Funding Identified'),
)
PROJECT_END_CHOICES = (
    ('Be completed', 'Be completed'),
    ('Require additional funding', 'Require additional funding'),
)
CLASSIFICATION_CHOICES = (
    ('Prime applicant','Prime applicant'),
    ('Pass-through entity','Pass-through entity'),
)
TIME_FRAME_CHOICES = (
    ('One Year','One Year'),
    ('Multi-Year','Multi-Year'),
)
PROJECT_TYPE_CHOICES = (
    ('Academic Support','Academic Support'),
    ('Institutional','Institutional'),
    ('Instructional','Instructional'),
    ('Outreach/Public Service','Outreach/Public Service'),
    ('Research','Research'),
)
SPONSOR_TYPE_CHOICES = (
    ('Federal','Federal'),
    ('Foundation','Foundation'),
    ('State','State'),
    ('Corporation','Corporation'),
    ('Other','Other'),
)
TERM_CHOICES = (
    ('Summer','Summer'),
    ('Academic Year','Academic Year'),
    ('Both','Both'),
)
PROPOSAL_STEPS_CHOICES = (
    ('','----------'),
    ('1','Part A'),
    ('2','Part B'),
    ('3','Parts A and B')
)
PROPOSAL_GOAL_CHOICES = (
    ('Goal','Goal'),
    ('Objective','Objective'),
    ('Outcome','Outcome'),
    ('Priority','Priority')
)
PROPOSAL_TYPE_CHOICES = (
    (
        'New: never submitted this proposal to this agency before',
        'New: never submitted this proposal to this agency before'
    ),
    (
        '''
            Revised Per Funder Request: update of submitted proposal,
            because funder requested changes
        ''',
        '''
            Revised Per Funder Request: update of submitted proposal,
            because funder requested changes
        '''
    ),
    (
        '''
            Re-Submission: submitted proposal in prior round of funding,
            re-submitting proposal for new round
        ''',
        '''
            Re-Submission: submitted proposal in prior round of funding,
            re-submitting proposal for new round
        '''
    ),
    ('Other','Other')
)

FUNDING_SOURCE_CHOICES = (
    ('Federal','Federal'),
    ('Foundation','Foundation'),
    ('State','State'),
    ('Corporation','Corporation'),
    ('Other','Other'),
)

INDIRECT_COST_RATE_CHOICES = (
    (
        'Carthage College Federally Negotiated Indirect Rate',
        'Carthage College Federally Negotiated Indirect Rate'
    ),
    (
        'Funding Agency will not allow Indirect Costs',
        'Funding Agency will not allow Indirect Costs'
    ),
    ('Other','Other'),
)

#    ('',''),
