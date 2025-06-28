def check_alias_reference_lambdai(table_aliases: 'list', standalone_aliases: 'list', this_ref_type: 'str', r: 'ColumnReferenceSegment') -> 'LintResult | None':
    """
    首先从{table_aliases}和{standalone_aliases}中获取所有的aliases。如果引用带前缀，即{this_ref_type}是'qualified'的，就从{r}中取出前缀，检查它是否在已有的aliases中。如果不符合，则返回一个LintResult来描述这个错误，它的cnchor是这个r。
    """
    from typing import List
    
    # Combine all aliases from both sources
    all_aliases = []
    for alias_info in table_aliases:
        all_aliases.append(alias_info.ref_str)
    for alias_info in standalone_aliases:
        all_aliases.append(alias_info.ref_str)
    
    # Only check qualified references
    if this_ref_type == 'qualified':
        # Get the prefix from the column reference
        prefix = r.get_identifier().parts[0]
        
        # Check if prefix exists in the combined aliases
        if prefix not in all_aliases:
            return LintResult(
                anchor=r,
                description=f"Invalid table alias '{prefix}'. Available aliases: {', '.join(all_aliases)}"
            )
    
    # Return None if no issues found
    return None