from typing import Dict, Any, List, Union
import os
import requests
from agents import function_tool

@function_tool(
    name_override="create_ticket",
    description_override="To create a ticket in a Google Spreadsheet.",
    strict_mode=True
)
def create_ticket(
    connection_id: str, 
    spreadsheet_id: str, 
    sheet_name: str, 
    row_data: List[Union[str, int, float, None]]
) -> Dict[str, Any]:
    """
    To create a ticket in a Google Spreadsheet.

    Args:
        connection_id: The Google connection ID from Nango.
        spreadsheet_id: The Google Spreadsheet ID.
        sheet_name: Name of the sheet to insert data.
        row_data: List representing the row to append.

    Returns:
        Dict containing the API response.
    """
    print("="*50)
    print(f"::::[TOOL CALLED] CREATE TICKET:::::")
    print(f"  - connection_id: {connection_id}")
    print(f"  - spreadsheet_id: {spreadsheet_id}")
    print(f"  - sheet_name: {sheet_name}")
    print(f"  - row_data: {row_data}")
    print("="*50)

    def get_connection_credentials(id: str, providerConfigKey: str):
        base_url = os.getenv("NANGO_BASE_URL")
        secret_key = os.getenv("NANGO_SECRET_KEY")
        url = f"{base_url}/connection/{id}"
        params = {
            "provider_config_key": providerConfigKey,
            "refresh_token": "true",
        }

        headers = {"Authorization": f"Bearer {secret_key}"}
        response = requests.request("GET", url, headers=headers, params=params)
        return response.json()

    class GoogleSheetsManager:
        @staticmethod
        def append_row(
            access_token: str, 
            spreadsheet_id: str, 
            sheet_name: str, 
            row_data: List[Union[str, int, float, None]]
        ) -> Dict[str, Any]:
            """
            Append a row to an existing Google Spreadsheet.

            Args:
                access_token: OAuth2 access token.
                spreadsheet_id: ID of the spreadsheet.
                sheet_name: Name of the sheet to append data into.
                row_data: List representing the row data (e.g., ["Alice", 25, "USA"]).

            Returns:
                Dict containing the API response or an error message.
            """
            try:
                url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}!A:A:append?valueInputOption=RAW"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                }
                payload = {"values": [row_data]}

                # Make the API request to append data
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                response.raise_for_status()

                if response.status_code == 200:
                    return {
                        "status": "success",
                        "response": response.json(),
                        "error": None,
                    }
                else:
                    return {
                        "status": "failed",
                        "response": None,
                        "error": f"Unexpected status code: {response.status_code}",
                    }

            except Exception as e:
                return {"status": "failed", "response": None, "error": str(e)}

    try:
        # Retrieve access token using Nango
        credentials = get_connection_credentials(
            id=connection_id, 
            providerConfigKey="google-sheet"
        )
        access_token = credentials["credentials"]["access_token"]

        # Append the row to the spreadsheet
        sheets_manager = GoogleSheetsManager()
        return sheets_manager.append_row(
            access_token=access_token,
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            row_data=row_data,
        )

    except Exception as e:
        error_message = f"Error in Google Sheets append row script: {e}"
        return {"status": "failed", "response": None, "error": error_message}
