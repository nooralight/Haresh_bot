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
                            "time": {
                                "description": "get user's input time",
                                "title": "Input time",
                                "type": "string"
                            }
                        },
                        "required": [
                            "date",
                            "time"
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
                            "time": {
                                "description": "get user's input time",
                                "title": "Input time",
                                "type": "string"
                            },
                            "padel_name": {
                                "description": "get user's input pedal name",
                                "title": "Input pedal match name",
                                "type": "string"
                            } 
                        },
                        "required": [
                            "date",
                            "time",
                            "padel_name"
                        ],
                        "type": "object"
                    }
                }
            }

show_padel_event = {
                "type": "function",
                "function": {
                    "name": "show_pedal_event",
                    "description":  "If user wants to check a padel match booking, or give you booking ID or number. This means the user wants to see details of the Match booking.",
                    "parameters": {
                        "properties": {
                            "booking_id": {
                                "description": "get the booking ID number",
                                "title": "Booking number",
                                "type": "string"
                            }
                        },
                        "required": [
                            "booking_id"
                        ],
                        "type": "object"
                    }
                }
            }


cancel_padel_event = {
                "type": "function",
                "function": {
                    "name": "cancel_pedal_event",
                    "description":  "If user wants to cancel a padel match booking, or give you booking ID or number to cencel it.",
                    "parameters": {
                        "properties": {
                            "booking_id": {
                                "description": "get the booking ID number",
                                "title": "Booking number",
                                "type": "string"
                            }
                        },
                        "required": [
                            "booking_id"
                        ],
                        "type": "object"
                    }
                }
            }