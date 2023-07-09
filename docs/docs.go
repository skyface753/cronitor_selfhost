// Code generated by swaggo/swag. DO NOT EDIT.

package docs

import "github.com/swaggo/swag"

const docTemplate = `{
    "schemes": {{ marshal .Schemes }},
    "swagger": "2.0",
    "info": {
        "description": "{{escape .Description}}",
        "title": "{{.Title}}",
        "contact": {},
        "version": "{{.Version}}"
    },
    "host": "{{.Host}}",
    "basePath": "{{.BasePath}}",
    "paths": {
        "/cron/result": {
            "post": {
                "description": "Result from the runner script",
                "consumes": [
                    "application/json"
                ],
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "Jobs"
                ],
                "summary": "CronJobResult",
                "parameters": [
                    {
                        "description": "CronJobResult",
                        "name": "CronJobResult",
                        "in": "body",
                        "required": true,
                        "schema": {
                            "$ref": "#/definitions/main.CronJobResult"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "type": "string"
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "type": "string"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "type": "string"
                        }
                    }
                }
            }
        },
        "/cron/status": {
            "get": {
                "description": "Get all the data for all jobs",
                "consumes": [
                    "application/json"
                ],
                "tags": [
                    "Jobs"
                ],
                "summary": "Get all the data for all jobs",
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "$ref": "#/definitions/influx.UptimeDataForAllJobsMap"
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "type": "object"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "type": "object"
                        }
                    }
                }
            }
        },
        "/cron/status/job/{jobID}": {
            "get": {
                "description": "Get all data for a job",
                "consumes": [
                    "application/json"
                ],
                "tags": [
                    "Jobs"
                ],
                "summary": "Get all data for a job",
                "parameters": [
                    {
                        "type": "string",
                        "description": "Job ID",
                        "name": "jobID",
                        "in": "path",
                        "required": true
                    }
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "$ref": "#/definitions/influx.UptimeDataMap"
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "type": "object"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "type": "object"
                        }
                    }
                }
            }
        },
        "/cron/status/last": {
            "get": {
                "description": "Get last data for all jobs",
                "consumes": [
                    "application/json"
                ],
                "tags": [
                    "Jobs"
                ],
                "summary": "Get last data for all jobs",
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "type": "object"
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "type": "object"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "type": "object"
                        }
                    }
                }
            }
        },
        "/cron/status/waiting": {
            "get": {
                "description": "Get all waiting jobs",
                "consumes": [
                    "application/json"
                ],
                "tags": [
                    "Jobs"
                ],
                "summary": "Get all waiting jobs",
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/config.Job"
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "type": "object"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "type": "object"
                        }
                    }
                }
            }
        },
        "/trigger/{jobID}": {
            "get": {
                "description": "Trigger a check for a job",
                "consumes": [
                    "application/json"
                ],
                "tags": [
                    "Jobs"
                ],
                "summary": "Trigger a check for a job",
                "parameters": [
                    {
                        "type": "string",
                        "description": "Job ID",
                        "name": "jobID",
                        "in": "path",
                        "required": true
                    }
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "type": "string"
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "type": "object"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "type": "object"
                        }
                    }
                }
            }
        }
    },
    "definitions": {
        "config.Duration": {
            "type": "object",
            "properties": {
                "time.Duration": {
                    "type": "integer"
                }
            }
        },
        "config.Job": {
            "type": "object",
            "properties": {
                "cron": {
                    "type": "string"
                },
                "grace_time": {
                    "description": "In seconds",
                    "allOf": [
                        {
                            "$ref": "#/definitions/config.Duration"
                        }
                    ]
                },
                "job_id": {
                    "type": "string"
                }
            }
        },
        "influx.UptimeData": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string"
                },
                "success": {
                    "type": "boolean"
                }
            }
        },
        "influx.UptimeDataForAllJobsMap": {
            "type": "object",
            "additionalProperties": {
                "$ref": "#/definitions/influx.UptimeDataMap"
            }
        },
        "influx.UptimeDataMap": {
            "type": "object",
            "additionalProperties": {
                "$ref": "#/definitions/influx.UptimeData"
            }
        },
        "main.CronJobResult": {
            "type": "object",
            "properties": {
                "api_key": {
                    "type": "string"
                },
                "error": {
                    "type": "string"
                },
                "job_id": {
                    "type": "string"
                },
                "success": {
                    "type": "boolean"
                }
            }
        }
    }
}`

// SwaggerInfo holds exported Swagger Info so clients can modify it
var SwaggerInfo = &swag.Spec{
	Version:          "1.0.0",
	Host:             "localhost:8080",
	BasePath:         "/api/v1",
	Schemes:          []string{},
	Title:            "User API documentation",
	Description:      "",
	InfoInstanceName: "swagger",
	SwaggerTemplate:  docTemplate,
	LeftDelim:        "{{",
	RightDelim:       "}}",
}

func init() {
	swag.Register(SwaggerInfo.InstanceName(), SwaggerInfo)
}