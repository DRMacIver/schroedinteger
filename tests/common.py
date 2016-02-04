from hypothesis import strategies as st
from schroedinteger import schroedinteger

schroedintegers = st.builds(
    lambda x, _: schroedinteger(x),
    st.lists(st.integers(), min_size=1, average_size=5) | st.none(),
    st.random_module()
)

mixed_integers = schroedintegers | st.integers()
