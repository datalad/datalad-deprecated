from datalad.support.constraints import EnsureChoice
from datalad.support.param import Parameter


reporton_opt = Parameter(
    args=('--reporton',),
    metavar='TYPE',
    doc="""choose on what type result to report on: 'datasets',
    'files', 'all' (both datasets and files), or 'none' (no report).""",
    constraints=EnsureChoice('all', 'datasets', 'files', 'none')
)
