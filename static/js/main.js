console.log("asd");
// give reference to "Go Search" button
var go_search = d3.select("#submit");


go_search.on("click", function(){
    d3.event.preventDefault();
    
    // grab input value and store into variable
    var title = d3.select("#job-title").node().value;
    var loc = d3.select("#job-loc").node().value;
    
    // refresh search bars
    d3.select("#job-title").node().value = "";
    d3.select("#job-loc").node().value = "";
    console.log(title);
    console.log(loc);


    // Since HTTP only allow to send string we split title and location by "/" which
    // we will split in python to separate two words.
    var input = title +"!" + loc
    console.log(input);
   
    // send it off to scrape function 
    scrape(input);
})

function scrape(input){
    // send input to python
    var url = `/scrape/${input}`;
    d3.json(url).then(function(response){
        console.log(response);
    });
};