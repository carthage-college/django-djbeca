# -*- coding: utf-8 -*-

from djtools.fields import BINARY_CHOICES


UNSURE_CHOICES = (
    BINARY_CHOICES[0],
    BINARY_CHOICES[1],
    ('Unsure', 'Unsure'),
)
FUNDING_CHOICES = (
    ('Pursuit of Funding', 'Pursuit of Funding'),
    ('Funding Identified', 'Funding Identified'),
)
PROJECT_END_CHOICES = (
    ('Be completed', 'Be completed'),
    ('Require additional funding', 'Require additional funding'),
)
CLASSIFICATION_CHOICES = (
    ('Prime applicant', 'Prime applicant'),
    ('Pass-through entity', 'Pass-through entity'),
)
TIME_FRAME_CHOICES = (
    ('One Year', 'One Year'),
    ('Multi-Year', 'Multi-Year'),
)
PROJECT_TYPE_CHOICES = (
    ('Academic Support', 'Academic Support'),
    ('Institutional', 'Institutional'),
    ('Instructional', 'Instructional'),
    ('Outreach/Public Service', 'Outreach/Public Service'),
    ('Research', 'Research'),
    ('Other', 'Other'),
)
SPONSOR_TYPE_CHOICES = (
    ('Federal', 'Federal'),
    ('Foundation', 'Foundation'),
    ('State', 'State'),
    ('Corporation', 'Corporation'),
    ('Other', 'Other'),
)
TERM_CHOICES = (
    ('Summer', 'Summer'),
    ('Academic Year', 'Academic Year'),
    ('Both', 'Both'),
)
PROPOSAL_STEPS_CHOICES = (
    ('', '----------'),
    ('1', 'Part A'),
    ('2', 'Part B'),
    ('3', 'Parts A and B'),
)
APPROVAL_LEVEL_CHOICES = (
    ('', '----------'),
    ('level3', 'Division Dean'),
    ('level2', 'CFO'),
    ('level1', 'Provost'),
)
PROPOSAL_GOAL_CHOICES = (
    ('Goal', 'Goal'),
    ('Objective', 'Objective'),
    ('Outcome', 'Outcome'),
    ('Priority', 'Priority'),
)
PROPOSAL_TYPE_CHOICES = (
    ('new', 'New'),
    ('revised', 'Revised'),
    ('resubmission', 'Re-Submission'),
    ('other', 'Other'),
)
FUNDING_SOURCE_CHOICES = (
    ('Federal', 'Federal'),
    ('Foundation', 'Foundation'),
    ('State', 'State'),
    ('Corporation', 'Corporation'),
    ('International', 'International'),
    ('Other', 'Other'),
)
INDIRECT_COST_RATE_CHOICES = (
    (
        'Carthage College Federally Negotiated Indirect Rate',
        'Carthage College Federally Negotiated Indirect Rate',
    ),
    (
        'Funding Agency will not allow Indirect Costs',
        'Funding Agency will not allow Indirect Costs',
    ),
    ('Other', 'Other'),
)
LEAD_INSTITUTION_CHOICES = (
    ('lead', 'Lead Institution'),
    ('collaborative', 'Collaborative Partner'),
    ('subrecipient', 'Subrecipient'),
    ('contractual', 'Contractual Partner'),
)
STUDENTS_INVOLVED_CHOICES = (
    ('Student Payout', 'Student Payout'),
    ('Student Room/Board', 'Room/Board'),
    ('Student Travel', 'Student Travel'),
    ('None', 'None'),
)
PERSONNEL_SALARY_CHOICES = (
    ('Academic Year', 'Academic Year'),
    ('Summer Months', 'Summer Months'),
    ('Both', 'Both'),
    ('None', 'None'),
)
FUNDS_CHOICES = (
    ('New Funds', 'New Funds'),
    ('Exisiting Funds', 'Exisiting Funds'),
)
