from klibs.KLIndependentVariable import IndependentVariableSet

SSAT_line_ind_vars = IndependentVariableSet()

SSAT_line_ind_vars.add_variable("set_size", int, [8,12,16,20])
SSAT_line_ind_vars.add_variable("present_absent", str, ['present', 'absent'])