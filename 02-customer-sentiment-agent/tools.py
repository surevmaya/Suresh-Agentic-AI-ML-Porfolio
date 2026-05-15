TOOLS = [
    {
        "name": "search_vendor_news",
        "description": "Search recent news about SAP including financial health, stock performance, legal issues and competitor activity",
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor": {
                    "type": "string",
                    "description": "Name of the software vendor SAP"
                },
                "product": {
                    "type": "string",
                    "description": "Name of the product S/4HANA"
                }
            },
            "required": ["vendor", "product"]
        }
    },
    {
        "name": "search_vendor_reviews",
        "description": "Search for customer reviews and user experiences including complaints, frustrations and satisfaction levels",
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor": {
                    "type": "string",
                    "description": "Name of the software vendor SAP"
                },
                "product": {
                    "type": "string",
                    "description": "Name of the product S/4HANA"
                }
            },
            "required": ["vendor", "product"]
        }
    }
]
