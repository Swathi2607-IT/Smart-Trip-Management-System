<?php
require_once 'includes/db.php';
session_start();

if(!isset($_SESSION['user_id']) || $_SERVER['REQUEST_METHOD'] != 'POST') {
    header("Location: destinations.php");
    exit;
}

$dest_id = $_POST['dest_id'];
$start_date = $_POST['start_date'];
$duration = (int)$_POST['duration'];
$trip_start_mode = $_POST['trip_start_mode'];
$transport_id = (int)$_POST['transport_id'];

// Get Destination Details
$stmt = $pdo->prepare("SELECT * FROM destinations WHERE id = ?");
$stmt->execute([$dest_id]);
$destination = $stmt->fetch();

// Get Transport Details
$transport_cost = 0;
$transport_mode = 'None';
if($transport_id > 0) {
    $tStmt = $pdo->prepare("SELECT * FROM transports WHERE id = ?");
    $tStmt->execute([$transport_id]);
    $tData = $tStmt->fetch();
    if($tData) {
        $transport_cost = $tData->average_cost;
        $transport_mode = $tData->mode;
    }
}

// Logic for Trip Start & Duration Extrapolation
$startDateObj = new DateTime($start_date);
$package_cost = $duration * $destination->base_price;
$total_cost = $package_cost + $transport_cost;

if($trip_start_mode === 'After Arrival') {
    // Arrival takes 1 day, then trip duration begins
    // Trip Start: Day 2. Trip Ends: Day (2 + duration)
    // Extra 1 day of travel buffer added visually.
    $actual_start_date = clone $startDateObj;
    $actual_start_date->modify('+1 day');
    
    $end_date_obj = clone $actual_start_date;
    $end_date_obj->modify('+' . ($duration - 1) . ' days'); // Duration includes the first full day of start
} else {
    // Includes Travel: Trip starts on start_date
    $actual_start_date = clone $startDateObj;
    $end_date_obj = clone $actual_start_date;
    $end_date_obj->modify('+' . ($duration - 1) . ' days');
}

$end_date = $end_date_obj->format('Y-m-d');
$actual_start_date_str = $actual_start_date->format('Y-m-d');

// Insert Pending Booking Record
$stmt = $pdo->prepare("INSERT INTO bookings 
    (user_id, destination_id, start_date, duration, end_date, trip_start_mode, transport_mode, transport_cost, package_cost, total_cost, status, payment_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', 'Unpaid')"
);

$stmt->execute([
    $_SESSION['user_id'], $destination->id, $actual_start_date_str, $duration, $end_date, 
    $trip_start_mode, $transport_mode, $transport_cost, $package_cost, $total_cost
]);

$booking_id = $pdo->lastInsertId();

require_once 'includes/header.php';
?>

<div class="container section">
    <div style="max-width: 600px; margin: 0 auto;">
        
        <div class="alert alert-success">
            ✅ <strong>Price Calculation Module:</strong> The total cost of the trip has been calculated dynamically based on your transport selection and duration logic.
        </div>
        
        <div class="glass-panel mt-4">
            <h2 class="mb-4">Order Breakdown & Pricing</h2>
            <div style="border-bottom: 2px solid var(--gray-200); padding-bottom: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Package Rate per Day</span>
                    <span>₹<?= number_format($destination->base_price) ?></span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Number of Days (Duration)</span>
                    <span><?= $duration ?> Days</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Package Base Cost</span>
                    <strong>₹<?= number_format($package_cost) ?></strong>
                </div>
            </div>

            <div style="border-bottom: 2px solid var(--gray-200); padding-bottom: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Transport Selection (<?= htmlspecialchars($transport_mode) ?>)</span>
                    <span>₹<?= number_format($transport_cost) ?></span>
                </div>
            </div>

            <div style="border-bottom: 2px solid var(--gray-200); padding-bottom: 1rem; margin-bottom: 1rem; font-size: 0.9rem; color: var(--gray-500);">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Travel Date Selected:</span>
                    <span><?= $startDateObj->format('d M Y') ?></span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Trip Start Mode:</span>
                    <span class="badge" style="background: var(--light); color: var(--dark)"><?= htmlspecialchars($trip_start_mode) ?></span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Actual Trip Start:</span>
                    <strong style="color: var(--primary);"><?= $actual_start_date->format('d M Y') ?></strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Expected Trip End:</span>
                    <strong style="color: var(--primary);"><?= $end_date_obj->format('d M Y') ?></strong>
                </div>
            </div>

            <div style="display: flex; justify-content: space-between; font-size: 1.5rem; font-weight: bold; margin-bottom: 2rem;">
                <span>Total Payable Amount</span>
                <span>₹<?= number_format($total_cost) ?></span>
            </div>

            <form method="POST" action="payment.php">
                <input type="hidden" name="booking_id" value="<?= $booking_id ?>">
                <button type="submit" class="btn btn-primary" style="width: 100%; font-size: 1.25rem;">Proceed to Payment Checkout</button>
            </form>
            <form method="POST" action="cancel_pending.php" class="mt-2">
                <input type="hidden" name="booking_id" value="<?= $booking_id ?>">
                <button type="submit" class="btn btn-danger" style="width: 100%; background: var(--gray-200); color: var(--dark);">Cancel Order</button>
            </form>
        </div>
    </div>
</div>

<?php require_once 'includes/footer.php'; ?>
