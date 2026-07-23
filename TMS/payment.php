<?php
require_once 'includes/db.php';
session_start();

if(!isset($_SESSION['user_id']) || !isset($_POST['booking_id'])) {
    header("Location: destinations.php");
    exit;
}

$booking_id = (int)$_POST['booking_id'];
$stmt = $pdo->prepare("SELECT * FROM bookings WHERE id = ? AND user_id = ? AND status = 'Pending'");
$stmt->execute([$booking_id, $_SESSION['user_id']]);
$booking = $stmt->fetch();

if(!$booking) {
    header("Location: my_bookings.php");
    exit;
}

// Simulated Payment Process
$payment_success = false;
$error = '';

if(isset($_POST['pay_now'])) {
    $transaction_id = 'UPI' . date('YmdHis') . rand(100, 999);
    $receipt_token = bin2hex(random_bytes(16));
    
    // Insert Payment & Update Booking
    try {
        $pdo->beginTransaction();
        
        $pStmt = $pdo->prepare("INSERT INTO payments (booking_id, transaction_id, amount, payment_method) VALUES (?, ?, ?, 'UPI')");
        $pStmt->execute([$booking_id, $transaction_id, $booking->total_cost]);
        
        // Randomly assign a guide if available
        $gStmt = $pdo->query("SELECT id FROM guides ORDER BY RAND() LIMIT 1");
        $guide_id = $gStmt->fetchColumn();

        $bStmt = $pdo->prepare("UPDATE bookings SET status = 'Confirmed', payment_status = 'Paid', receipt_token = ?, guide_id = ? WHERE id = ?");
        $bStmt->execute([$receipt_token, $guide_id, $booking_id]);
        
        $pdo->commit();
        
        // Redirect to receipt
        header("Location: receipt.php?token=" . $receipt_token);
        exit;
    } catch(Exception $e) {
        $pdo->rollBack();
        $error = "Payment failed! Please try again.";
    }
}

require_once 'includes/header.php';
?>

<div class="container section">
    <div style="max-width: 500px; margin: 0 auto;">
        <div class="glass-panel text-center">
            <h2 class="mb-4">Complete Payment</h2>
            
            <?php if($error): ?>
                <div class="alert alert-danger"><?= htmlspecialchars($error) ?></div>
            <?php endif; ?>

            <div style="background: var(--light); padding: 20px; border-radius: 8px; margin-bottom: 2rem;">
                <p class="text-gray-500 mb-2">Total Amount Payable</p>
                <div style="font-size: 2.5rem; font-weight: bold; color: var(--primary);">₹<?= number_format($booking->total_cost) ?></div>
            </div>

            <p class="mb-4">Using Mock UPI Simulation</p>

            <form method="POST" action="payment.php">
                <input type="hidden" name="booking_id" value="<?= $booking_id ?>">
                <button type="submit" name="pay_now" class="btn btn-primary" style="width: 100%; font-size: 1.125rem;">Pay via UPI</button>
            </form>
            
            <form method="POST" action="cancel_pending.php" style="margin-top: 10px;">
                <input type="hidden" name="booking_id" value="<?= $booking_id ?>">
                <button type="submit" class="btn btn-secondary" style="width: 100%;">Cancel Payment</button>
            </form>

        </div>
    </div>
</div>

<?php require_once 'includes/footer.php'; ?>
