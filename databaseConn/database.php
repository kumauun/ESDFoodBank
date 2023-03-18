<?php
$servername = "http://db-savood.c0hav88yk9mq.us-east-1.rds.amazonaws.com";
$username = "admin";
$password = "rootroot";
$dbname = "test";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

$sql = "SELECT aid, aname, weight FROM assessment";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
  // output data of each row
  while($row = $result->fetch_assoc()) {
    echo "id: " . $row["aid"]. " - Name: " . $row["aname"]. " " . $row["weight"]. "<br>";
  }
} else {
  echo "0 results";
}
$conn->close();
?>