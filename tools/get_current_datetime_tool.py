from agents import function_tool

@function_tool(
    name_override="get_current_datetime",
    description_override="Get the current date and time in IST format.",
    strict_mode=True
)
def get_current_datetime():
    from datetime import datetime
    from zoneinfo import ZoneInfo
    print("="*50)   
    print("::::[TOOL CALLED] GET CURRENT DATETIME::::")
    print("="*50)
    ist = ZoneInfo("Asia/Kolkata")
    current_datetime = datetime.now(ist)
    formatted_datetime = current_datetime.strftime("%d-%b-%y %I:%M %p IST")
    return formatted_datetime
