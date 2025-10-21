provider "aws" {
  region = "us-east-1"
}

resource "aws_dynamodb_table" "sensor_data" {
  name           = "sensor-data"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "pk"
  range_key      = "ts"

  attribute {
    name = "pk"
    type = "S"
  }
  attribute {
    name = "ts"
    type = "N"
  }
  attribute {
    name = "metric_type"
    type = "S"
  }

  # Optional GSI to get "latest across all devices" per metric
  global_secondary_index {
    name               = "metric_ts"
    hash_key           = "metric_type"
    range_key          = "ts"
    projection_type    = "INCLUDE"
    non_key_attributes = ["device_id", "value", "unit", "date_ymd", "pk"]
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"
}