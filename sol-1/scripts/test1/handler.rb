require 'json'

def lambda_handler(event:, context:)
    # TODO implement
    puts event
    puts "----------------"
    puts context
    { statusCode: 200, body: JSON.generate('Lambda!') }
end
