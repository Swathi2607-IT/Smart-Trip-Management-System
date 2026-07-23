<?php
if(session_status() === PHP_SESSION_NONE) {
    session_start();
}
require_once '../includes/db.php';

if(!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'admin') {
    die("<div style='text-align:center; padding: 20px; font-family: sans-serif;'><h2>Access Denied</h2><p>You must be an administrator to view this page. <a href='../index.php'>Return to Home</a></p></div>");
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - TMS</title>
    <link rel="stylesheet" href="../css/style.css">
</head>
<body>

<nav class="navbar" style="background: rgba(30, 41, 59, 0.95); color: white;">
    <a href="index.php" class="nav-brand" style="color: white !important;">
        🛠️ TMS Admin
    </a>
    <ul class="nav-links">
        <li><a href="index.php" style="color: #cbd5e1;">Dashboard</a></li>
        <li><a href="manage_bookings.php" style="color: #cbd5e1;">Bookings</a></li>
        <li><a href="manage_destinations.php" style="color: #cbd5e1;">Destinations</a></li>
        <li><a href="manage_guides.php" style="color: #cbd5e1;">Guides</a></li>
        <li><a href="../index.php" class="nav-btn" style="background: var(--secondary);">Return to App</a></li>
    </ul>
</nav>

<main>
