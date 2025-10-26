provider "aws" {
  region = "us-east-1"
}

# --- (optional, handy) who/where am I
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

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

# --- IAM role that IoT Core will assume to write to DynamoDB
resource "aws_iam_role" "iot_to_dynamodb" {
  name = "iot-to-dynamodb"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Service = "iot.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

# --- Minimal permissions: allow PutItem to your table
resource "aws_iam_role_policy" "put_item_sensor_data" {
  name = "put-item-sensor-data"
  role = aws_iam_role.iot_to_dynamodb.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "AllowPutItem",
        Effect = "Allow",
        Action = ["dynamodb:PutItem"],
        Resource = aws_dynamodb_table.sensor_data.arn
      },
      # (nice to have for debugging the table in console flows)
      {
        Sid    = "DescribeTable",
        Effect = "Allow",
        Action = ["dynamodb:DescribeTable"],
        Resource = aws_dynamodb_table.sensor_data.arn
      }
    ]
  })
}

# --- IoT Topic Rule: writes each incoming message to DynamoDBv2 (PutItem)
# NOTE:
# 1) Your device MUST publish JSON containing: pk, ts, value, unit, device_id, metric_type, date_ymd, quality, ttl
# 2) Because we're using DynamoDBv2 PutItem, IoT will write each top-level field as a DDB attribute.
#    As long as your payload includes "pk" (string) and "ts" (number), it will satisfy the table's keys.
resource "aws_iot_topic_rule" "insert_sensor_data" {
  name        = "insert_sensor_data"
  description = "Insert telemetry into DynamoDB sensor-data table"
  enabled     = true
  sql_version = "2016-03-23"

  # Adjust the topic to match what you actually publish to
  # Example device payload:
  # {
  #   "pk": "10000000a6485bf1#temperature",
  #   "ts": 1761504563609,
  #   "value": 22.312,
  #   "unit": "C",
  #   "device_id": "10000000a6485bf1",
  #   "metric_type": "temperature",
  #   "date_ymd": "2025-10-26",
  #   "quality": "ok",
  #   "ttl": 1769280563
  # }
  sql = <<-SQL
    SELECT
      pk, ts, value, unit, device_id, metric_type, date_ymd, quality, ttl
    FROM 'pi-aqua-dreams/temperature'
  SQL

  dynamodbv2 {
    role_arn = aws_iam_role.iot_to_dynamodb.arn

    put_item {
      # With DynamoDBv2, specifying table_name is enough:
      # IoT uses the fields selected by the SQL as the item attributes.
      table_name = aws_dynamodb_table.sensor_data.name
    }
  }

  # Ensure the DDB policy exists before the rule activates
  depends_on = [aws_iam_role_policy.put_item_sensor_data]
}
