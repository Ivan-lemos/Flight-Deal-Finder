GOAL
We will use a combination of different APIs to create a cheap flight finder.
We maintain a Google Sheet that tracks locations we want to visit along with a price cutoff representing a historical low price.
For example, I might want to visit Kerala and Kochi to enjoy South Indian cuisine, setting a price limit of 350 pounds return from London.
This data is fed into a flight search API that runs daily, searching all locations for the cheapest flights in the next six months.
When the API finds a flight cheaper than our predefined price, it sends the date and price via Twilio SMS to our mobile phone so we can book immediately.

Use Sheety to read and write data to the Google Sheet
Get the IATA codes using Amadeus
Search for cheap flights
If price is lower than in the sheet, send the message(SMS/WhatsApp)

The message should include:

Price

Departure Airport IATA Code

Arrival Airport IATA Code

Outbound Date

Inbound Date

Key Takeaways
Developed a flight finder program using multiple APIs to discover affordable flight deals.
Utilized a Google Sheet to track desired travel locations and their historical low prices.
Automated daily flight searches for the next six months to identify flights cheaper than predefined price thresholds.
Integrated Twilio SMS to send instant low price alerts for booking opportunities.

CHALLENGES
Upgraded the Flight Deal Hunter project to a full product with user sign-up and email notifications.
Introduced the concept of building a company around the project, replicating services like Jack's Flight Club.
Implemented user input validation and storage of user data in a spreadsheet.
Utilized the SMTP module to send daily emails with the latest flight deals to users.
