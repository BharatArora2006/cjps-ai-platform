def generate_case_summary(data):

    summary = f"""
    Process service case for
    {data.get('defendant_name', 'Unknown Defendant')}.

    Client:
    {data.get('client_name', 'Unknown Client')}.

    County:
    {data.get('county', 'Unknown County')}.

    Address:
    {data.get('address', 'No Address')}.

    Instructions:
    {data.get('instructions', 'None')}.
    """

    return summary.strip()