let request = new XMLHttpRequest();

request.onreadystatechange = function(){
    if (this.readyState === 4 && this.status === 200){
        document.getElementById("start").innerHTML = this.response;
    }

};
request.open("GET", "/data/submissions.txt");
request.send();

sendData = ()=> {
    let post = new XMLHttpRequest();

    const name = document.getElementById("AjaxName")
    const age = document.getElementById("AjaxAge")

    const _name = name.value;
    const _age = age.value;

    post.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            document.getElementById("start").innerHTML = "Form was submitted!";
        }
    };
    post.open("POST", "/data/contents.json");
    const data = {"Name":_name,"Age":_age};
    post.send(JSON.stringify(data));
}