<?php
require_once 'includes/db.php';
session_start();

if(!isset($_SESSION['user_id']) || !isset($_GET['id'])) {
    header("Location: my_bookings.php");
    exit;
}

$booking_id = (int)$_GET['id'];
$user_id = $_SESSION['user_id'];

$stmt = $pdo->prepare("SELECT * FROM bookings WHERE id = ? AND user_id = ? AND status = 'Confirmed'");
$stmt->execute([$booking_id, $user_id]);
$booking = $stmt->fetch();

if(!$booking) {
    header("Location: my_bookings.php");
    exit;
}

// Logic: Cancellation Refund Policies
$today = new DateTime();
$tripStart = new DateTime($booking->start_date);
$daysDiff = $today->diff($tripStart)->days;
$refund_amount = 0;

if($today >= $tripStart) {
    // Cannot cancel after start date
    header("Location: my_bookings.php?msg=Cancellation not allowed after trip has started.");
    exit;
}

if($daysDiff > 5) {
    $refund_amount = $booking->total_cost; // 100%
} elseif($daysDiff >= 2 && $daysDiff <= 5) {
    $refund_amount = $booking->total_cost * 0.5; // 50%
} else {
    $refund_amount = 0; // Less than 2 days, 0% refund
}

$error = '';
if(isset($_POST['confirm_cancel'])) {
    
    try {
        $pdo->beginTransaction();
        // Update booking
        $cStmt = $pdo->prepare("UPDATE bookings SET status = 'Cancelled', refund_amount = ?, cancellation_date = NOW() WHERE id = ?");
        $cStmt->execute([$refund_amount, $booking_id]);

        // Optional: Update payments table status to 'Refunded'
        $pStmt = $pdo->prepare("UPDATE payments SET payment_method = 'Refund Processed' WHERE booking_id = ?");
        $pStmt->execute([$booking_id]);

        $pdo->commit();
        header("Location: my_bookings.php?msg=Trip successfully cancelled. Refund processed: ₹" . number_format($refund_amount));
        exit;
    } catch(Exception $e) {
        $pdo->rollBack();
        $error = "Error processing cancellation.";
    }
}

require_once 'includes/header.php';
?>

<div class="container section">
    <div style="max-width: 600px; margin: 0 auto;">
        
        <?php if($error): ?>
            <div class="alert alert-danger"><?= htmlspecialchars($error) ?></div>
        <?php endif; ?>

        <div class="glass-panel text-center border: 1px solid var(--error);">
            <h2 class="mb-2" style="color: var(--error);">Confirm Cancellation</h2>
            <p class="mb-4">Are you sure you want to cancel booking <strong>#<?= $booking->id ?></strong>?</p>
            
            <div style="background: var(--light); padding: 20px; border-radius: 8px; margin-bottom: 2rem; text-align: left;">
                <p><strong>Total Paid:</strong> ₹<?= number_format($booking->total_cost) ?></p>
                <p><strong>Days until trip:</strong> <?= $daysDiff ?> days</p>
                
                <hr style="margin: 10px 0;">
                <p><strong>Refund Policy:</strong></p>
                <ul style="margin-left: 20px; font-size: 0.9rem; color: var(--gray-500);">
                    <li>More than 5 days: 100% refund</li>
                    <li>2 - 5 days: 50% refund</li>
                    <li>Less than 2 days: 0% refund</li>
                </ul>
                <hr style="margin: 10px 0;">
                <p style="font-size: 1.25rem;"><strong>Eligible Refund Amount: <span style="color: var(--secondary);">₹<?= number_format($refund_amount) ?></span></strong></p>
            </div>

            <form method="POST" action="cancel_booking.php?id=<?= $booking->id ?>" style="display: flex; gap: 10px;">
                <a href="my_bookings.php" class="btn btn-secondary" style="flex: 1;">No, keep my trip</a>
                <button type="submit" name="confirm_cancel" class="btn btn-danger" style="flex: 1;">Yes, Cancel Trip</button>
            </form>
        </div>

    </div>
</div>

<?php require_once 'includes/footer.php'; ?>
