# IAM role that IoT Core will assume to write to DynamoDB
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

# Minimal permissions: allow PutItem to your table (+ Describe for convenience)
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
      {
        Sid    = "DescribeTable",
        Effect = "Allow",
        Action = ["dynamodb:DescribeTable"],
        Resource = aws_dynamodb_table.sensor_data.arn
      }
    ]
  })
}
