<?php
if(session_status() === PHP_SESSION_NONE) {
    session_start();
}
require_once 'db.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trip Management System</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>

<nav class="navbar">
    <a href="index.php" class="nav-brand">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-compass"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>
        TMS Journey
    </a>
    <ul class="nav-links">
        <li><a href="index.php">Home</a></li>
        <li><a href="destinations.php">Destinations</a></li>
        
        <?php if(isset($_SESSION['user_id'])): ?>
            <li><a href="my_bookings.php">My Bookings</a></li>
            <?php if((isset($_SESSION['role']) ? $_SESSION['role'] : '') === 'admin'): ?>
                <li><a href="admin/index.php" class="badge" style="background:var(--error);color:white;">Admin Panel</a></li>
            <?php endif; ?>
            <li><a href="logout.php" class="nav-btn">Logout (<?= htmlspecialchars(isset($_SESSION['name']) ? $_SESSION['name'] : 'User') ?>)</a></li>
        <?php else: ?>
            <li><a href="login.php">Login</a></li>
            <li><a href="register.php" class="nav-btn">Sign Up</a></li>
        <?php endif; ?>
    </ul>
</nav>

<main>
