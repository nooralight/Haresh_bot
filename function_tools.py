see_available_padels = {
                "type": "function",
                "function": {
                    "name": "check_available_padel",
                    "description": "Get date and time to check the available padels",
                    "parameters": {
                        "properties": {
                            "date": {
                                "description": "get user's input date",
                                "title": "Input date",
                                "type": "string"
                            },
                            "time_range": {
                                "description": "get user's input time range",
                                "title": "Input time range",
                                "type": "string"
                            }
                        },
                        "required": [
                            "date",
                            "time_range"
                        ],
                        "type": "object"
                    }
                }
            }

make_padel_event = {
                "type": "function",
                "function": {
                    "name": "make_padel_event",
                    "description": "Make padel match event",
                    "parameters": {
                        "properties": {
                            "date": {
                                "description": "get user's input date",
                                "title": "Input date",
                                "type": "string"
                            },
                            "time_range": {
                                "description": "get user's input time range",
                                "title": "Input time range",
                                "type": "string"
                            },
                            "padel_court_name": {
                                "description": "get user's input padel court name",
                                "title": "Input padel court name",
                                "type": "string"
                            } 
                        },
                        "required": [
                            "date",
                            "time_range",
                            "padel_court_name"
                        ],
                        "type": "object"
                    }
                }
            }

show_padel_event = {
                "type": "function",
                "function": {
                    "name": "show_pedal_event",
                    "description":  "If user wants to check a padel match booking, or give you match number. This means the user wants to see details of the Match booking.",
                    "parameters": {
                        "properties": {
                            "match_number": {
                                "description": "get the match number",
                                "title": "Match number",
                                "type": "string"
                            }
                        },
                        "required": [
                            "match_number"
                        ],
                        "type": "object"
                    }
                }
            }


cancel_padel_event = {
                "type": "function",
                "function": {
                    "name": "cancel_pedal_event",
                    "description":  "If user wants to cancel a padel match booking, or give you match number to cencel it.",
                    "parameters": {
                        "properties": {
                            "match_number": {
                                "description": "get the booking ID number",
                                "title": "Match number",
                                "type": "string"
                            }
                        },
                        "required": [
                            "match_number"
                        ],
                        "type": "object"
                    }
                }
            }