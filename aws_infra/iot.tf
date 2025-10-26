resource "aws_iot_topic_rule" "insert_sensor_data" {
  name        = "insert_sensor_data"
  description = "Insert telemetry into DynamoDB sensor-data table"
  enabled     = true
  sql_version = "2016-03-23"

  # Adjust the topic to match what you publish to
  sql = <<-SQL
    SELECT
      pk, ts, value, unit, device_id, metric_type, date_ymd, quality, ttl
    FROM 'pi-aqua-dreams/temperature'
  SQL

  dynamodbv2 {
    role_arn = aws_iam_role.iot_to_dynamodb.arn
    put_item {
      table_name = aws_dynamodb_table.sensor_data.name
    }
  }

  depends_on = [aws_iam_role_policy.put_item_sensor_data]
}
