var lastProjectDateTime = "";

$(document).ready(function () {
  checkLastProjectCreationDate();

  $("#new-project-form").submit(function (event) {
    if (compareDateTime() === false) {
      $("#submit-button")[0].setCustomValidity("Please wait a minute before creating another project.");
      $("#submit-button")[0].reportValidity();
      event.preventDefault();
      return false;
    }
  });
});

function checkLastProjectCreationDate() {
  var ajax = new XMLHttpRequest();
  ajax.onreadystatechange = function () {
    if (ajax.readyState === 4 && ajax.status == 200) {
      var response = ajax.response;
      if (response != "") {
        lastProjectDateTime = toJSDate(response);
      }
    }
  };
  ajax.open("POST", "/check_last_project", true);
  ajax.send();
}

function compareDateTime() {
  let date = new Date();
  let currentDateTime = date.getDate() + "-" + (
  date.getMonth() + 1) + "-" + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes();

  var currentDateTimeJS = toJSDate(currentDateTime);

  var timeDifference = Date.parse(currentDateTimeJS) - Date.parse(lastProjectDateTime);
  if (timeDifference < 60000) {
    //one minute in milliseconds
    return false;
  } else {
    return true;
  }
}

// Convert DateTime (dd-mm-yyyy hh-mm) to javascript DateTime
// Ex: 16-11-2015 16:05
// https://community.spiceworks.com/topic/1295639-compare-datetimes-in-jquery-javascript
function toJSDate(dateTime) {
  var dateTime = dateTime.split(" "); // dateTime[0] = date, dateTime[1] = time
  var date = dateTime[0].split("-");
  var time = dateTime[1].split(":");

  // (year, month, day, hours, minutes, seconds, milliseconds)
  // Subtract 1 from month because Jan is 0 and Dec is 11
  return new Date(date[2], date[1] - 1, date[0], time[0], time[1], 0, 0);
}
