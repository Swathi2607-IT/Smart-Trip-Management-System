<?php
$host = 'localhost';
$dbname = 'trip_management';
$user = 'root'; // Default Laragon user
$pass = 'Akisar@25'; // Default Laragon empty password

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $user, $pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    // Fetch objects by default for cleaner syntax
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_OBJ);
} catch (PDOException $e) {
    die("<div style='text-align:center; padding: 20px; font-family: sans-serif;'><h2>Database Connection Failed</h2><p>Please ensure you have imported the schema.sql in Laragon/phpMyAdmin.</p><p>Error: " . $e->getMessage() . "</p></div>");
}
?>
