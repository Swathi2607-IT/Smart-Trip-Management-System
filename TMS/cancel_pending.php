<?php
require_once 'includes/db.php';
session_start();

if(isset($_SESSION['user_id']) && isset($_POST['booking_id'])) {
    $stmt = $pdo->prepare("DELETE FROM bookings WHERE id = ? AND user_id = ? AND status = 'Pending'");
    $stmt->execute([$_POST['booking_id'], $_SESSION['user_id']]);
}

header("Location: destinations.php");
exit;
?>
