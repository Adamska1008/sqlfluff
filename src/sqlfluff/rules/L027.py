"""Implementation of Rule L027."""

from sqlfluff.core.rules.base import LintResult
from sqlfluff.rules.L020 import Rule_L020
from lambdai import AI

class Rule_L027(Rule_L020):
    """References should be qualified if select has more than one referenced table/view.

    .. note::
       Except if they're present in a ``USING`` clause.

    **Anti-pattern**

    In this example, the reference ``vee`` has not been declared,
    and the variables ``a`` and ``b`` are potentially ambiguous.

    .. code-block:: sql

        SELECT a, b
        FROM foo
        LEFT JOIN vee ON vee.a = foo.a

    **Best practice**

    Add the references.

    .. code-block:: sql

        SELECT foo.a, vee.b
        FROM foo
        LEFT JOIN vee ON vee.a = foo.a
    """

    def _lint_references_and_aliases(
        self,
        table_aliases,
        standalone_aliases,
        references,
        col_aliases,
        using_cols,
        parent_select,
    ):
        # Do we have more than one? If so, all references should be qualified.
        if len(table_aliases) <= 1:
            return None
        # A buffer to keep any violations.
        violation_buff = []
        # Check all the references that we have.
        for r in references:
            this_ref_type = r.qualification()
            # Discard column aliases that
            # refer to the current column reference.
            col_alias_names = [
                c.alias_identifier_name
                for c in col_aliases
                if r not in c.column_reference_segments
            ]
            if (
                this_ref_type == "unqualified"
                # Allow unqualified columns that
                # are actually aliases defined
                # in a different select clause element.
                and r.raw not in col_alias_names
                # Allow columns defined in a USING expression.
                and r.raw not in using_cols
            ):
                violation_buff.append(
                    LintResult(
                        anchor=r,
                        description=f"Unqualified reference {r.raw!r} found in "
                        "select with more than one referenced table/view.",
                    )
                )

        with AI:
            result: LintResult | None = AI.execute(
                "首先从{table_aliases}和{standalone_aliases}中获取所有的aliases。"
                "如果引用带前缀，即{this_ref_type}是'qualified'的，就从{r}中取出前缀，检查它是否在已有的aliases中。"
                "如果不符合，则返回一个LintResult来描述这个错误，它的cnchor是这个r。",
                table_aliases,
                standalone_aliases,
                this_ref_type,
                r
            )
            if result:
                violation_buff.append(result)
                
        return violation_buff or None
