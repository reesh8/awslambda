'use strict';

exports.handler = function(event, context) {
    var AWS = require('aws-sdk');
    AWS.config.update({region: 'us-west-2'});
    
    // var response = {
    //             statusCode: 200,
    //             headers: {
    //                 // "x-custom-header" : "my custom header value",
    //                 // "Access-Control-Allow-Origin": "*",
    //                 // "X-Requested-With":"*",
    //                 // "Access-Control-Allow-Headers": "Content-Type",
    //                 // "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    //             },
    //             body: JSON.stringify(event.message)
    //         };
    //         context.succeed(response);
    
    
    var lexruntime = new AWS.LexRuntime();
    var params = {
        botAlias: 'BETA',
        /* required */
        botName: 'DiningConcierge',
        /* required */
        inputText: event.message,
        /* required */
        userId: "11111",
        /* required */
        requestAttributes: {} /* This value will be JSON encoded on your behalf with JSON.stringify() */ ,
        sessionAttributes: {} /* This value will be JSON encoded on your behalf with JSON.stringify() */
    };
    lexruntime.postText(params, function(err, data) {
        if (err) {
            var responseCode = 500;
            var response = {
                statusCode: responseCode,
                headers: {
                    // "x-custom-header" : "my custom header value",
                    // "Access-Control-Allow-Origin": "*",
                    // "X-Requested-With":"*",
                    // "Access-Control-Allow-Headers": "Content-Type",
                    // "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
                },
                body: "999"+JSON.stringify(err)
            };
            context.succeed(response);
        }// an error occurred
        else {
            var responseCode = 200;
            var response = {
                statusCode: responseCode,
                headers: {
                    // "x-custom-header" : "my custom header value",
                    // "Access-Control-Allow-Origin": "*",
                    // "X-Requested-With":"*",
                    // "Access-Control-Allow-Headers": "Content-Type",
                    // "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
                },
                body: JSON.stringify(data.message)
            };
            //console.log(data); // successful response  
            context.succeed(response);
        }
    });
};