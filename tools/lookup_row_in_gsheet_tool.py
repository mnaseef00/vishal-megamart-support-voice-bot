from typing import Dict, Any
import os
import requests
from agents import function_tool

@function_tool(
    name_override="lookup_row_in_gsheet",
    description_override="To find a row by a lookup value in a Google Spreadsheet.",
    strict_mode=True
)
def lookup_row_in_gsheet(
    connection_id: str,
    spreadsheet_id: str,
    sheet_name: str,
    lookup_value: str,
    lookup_column: str,
) -> Dict[str, Any]:
    """
    To find a row by a lookup value in a Google Spreadsheet.

    Args:
        connection_id: The Google connection ID from Nango.
        spreadsheet_id: The Google Spreadsheet ID.
        sheet_name: Name of the sheet to search in.
        lookup_value: The value to search for.
        lookup_column: The column to search in.

    Returns:
        Dict containing the matched row and its index.
    """
    print("="*50)
    print(f"[TOOL CALLED] lookup_row_in_gsheet with parameters:")
    print(f"  - connection_id: {connection_id}")
    print(f"  - spreadsheet_id: {spreadsheet_id}")
    print(f"  - sheet_name: {sheet_name}")
    print(f"  - lookup_value: {lookup_value}")
    print(f"  - lookup_column: {lookup_column}")
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
        def find_row(
            access_token: str,
            spreadsheet_id: str,
            sheet_name: str,
            lookup_value: str,
            lookup_column: str,
        ) -> Dict[str, Any]:
            """
            Find a row by searching for a specific value in a given column.

            Args:
                access_token: OAuth2 access token.
                spreadsheet_id: ID of the spreadsheet.
                sheet_name: Name of the sheet to search.
                lookup_value: The value to search for.
                lookup_column: The column to search in.

            Returns:
                Dict containing the matched row, its index, or an error message.
            """
            try:
                url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}!{lookup_column}:{lookup_column}"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                }

                # Fetch all values in the lookup column
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                data = response.json().get("values", [])
                if not data:
                    return {
                        "status": "failed",
                        "row_index": None,
                        "row_data": None,
                        "error": "No data found in the sheet.",
                    }

                # Search for the lookup value
                for index, row in enumerate(
                    data, start=1
                ):  # Google Sheets is 1-based index
                    if row and row[0] == lookup_value:
                        row_url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}!{index}:{index}"
                        row_response = requests.get(
                            row_url, headers=headers, timeout=10
                        )
                        row_response.raise_for_status()
                        row_data = row_response.json().get("values", [[]])[0]

                        return {
                            "status": "success",
                            "row_index": index,
                            "row_data": row_data,
                            "error": None,
                        }

                return {
                    "status": "failed",
                    "row_index": None,
                    "row_data": None,
                    "error": "Lookup value not found.",
                }

            except Exception as e:
                return {
                    "status": "failed",
                    "row_index": None,
                    "row_data": None,
                    "error": str(e),
                }

    try:
        # Retrieve access token using Nango

        credentials = get_connection_credentials(
            id=connection_id, providerConfigKey="google-sheet"
        )
        access_token = credentials["credentials"]["access_token"]

        # Find the row in the spreadsheet
        sheets_manager = GoogleSheetsManager()
        return sheets_manager.find_row(
            access_token=access_token,
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            lookup_value=lookup_value,
            lookup_column=lookup_column,
        )

    except Exception as e:
        error_message = f"Error in Google Sheets find row script: {e}"
        return {
            "status": "failed",
            "row_index": None,
            "row_data": None,
            "error": error_message,
        }
