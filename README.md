Basic Python http server developed without the use of libraries.

My implementation is able to server HTML, CSS, JS and images upon request.

It also showcases being able to handle both GET and POST requests, and storing the contents of the POST request server side and being able to display it afterwards.

The possible contents that it can take from a POST request is a user supplied image which will be saved and can be displayed later as well as from a form.


The server is able to handle ajax and takes into account security by escaping and looking for special characters that are deemed risky.

There is some basic use of cookies, which keep track of returning users as well as some html templating.

So far I am working on getting websockets to work for now and may later work on appearance.

Its not pretty but it gets the job done, I was more focused on functionality than appearence when I developed it.
