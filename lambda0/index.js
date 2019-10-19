exports.handler = function(event, context) {
    var response;
    if (event.invocationSource == "FulfillmentCodeHook" && event.currentIntent.name == "DiningSuggestionsIntent") {
        response = {
            "dialogAction": {
                "fulfillmentState": "Fulfilled",
                "type": "Close",
                "message": {
                    "contentType": "PlainText",
                    "content": "You’re all set. Expect my suggestions shortly through an SMS! Have a good day! \n" 
                    // + JSON.stringify(event.currentIntent.slots)
                }
            }
        }

        var AWS = require('aws-sdk');
        AWS.config.update({region: 'us-west-2'});
        var sqs = new AWS.SQS();
        var params = {
            MessageAttributes: {
                "Title": {
                    DataType: "String",
                    StringValue: "The Whistler"
                },
                "Author": {
                    DataType: "String",
                    StringValue: "John Grisham"
                },
                "WeeksOn": {
                    DataType: "Number",
                    StringValue: "6"
                }
            },
            MessageBody: JSON.stringify(event.currentIntent.slots),
            QueueUrl: "https://sqs.us-west-2.amazonaws.com/735049541501/DiningOrders"
        };

        sqs.sendMessage(params, function(err, data) {
            if (err) {
                console.log("Error", err);
                context.succeed(err);
            }
            else {
                console.log("Success", data.MessageId);
                context.succeed(response);
            }
        });

    }
};
