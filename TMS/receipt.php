<?php
require_once 'includes/db.php';
session_start();

if(!isset($_GET['token'])) {
    header("Location: my_bookings.php");
    exit;
}

$token = $_GET['token'];

$stmt = $pdo->prepare("
    SELECT 
        b.*, 
        d.name as dest_name, 
        u.name as traveler_name, 
        u.email as traveler_email,
        g.name as guide_name,
        g.phone as guide_phone,
        p.transaction_id,
        p.payment_date
    FROM bookings b
    JOIN destinations d ON b.destination_id = d.id
    JOIN users u ON b.user_id = u.id
    LEFT JOIN guides g ON b.guide_id = g.id
    LEFT JOIN payments p ON b.id = p.booking_id
    WHERE b.receipt_token = ?
");

$stmt->execute([$token]);
$receipt = $stmt->fetch();

if(!$receipt) {
    die("Invalid receipt token.");
}

// Ensure the user viewing is either the owner or an admin
if(isset($_SESSION['user_id']) && $_SESSION['role'] !== 'admin' && $_SESSION['user_id'] != $receipt->user_id) {
    die("Unauthorized.");
}

require_once 'includes/header.php';
?>

<div class="container section">
    
    <div style="display: flex; justify-content: space-between; align-items: center;" class="mb-4">
        <h2>Booking Receipt #<?= $receipt->id ?></h2>
        <span class="badge status-confirmed">Confirmed & Paid</span>
    </div>

    <div class="grid" style="grid-template-columns: 2fr 1fr;">
        <div class="glass-panel">
            <h3 class="mb-3">Traveler & Journey Details</h3>
            <p><strong>Traveler Name:</strong> <?= htmlspecialchars($receipt->traveler_name) ?> (<?= htmlspecialchars($receipt->traveler_email) ?>)</p>
            <p><strong>Destination:</strong> <?= htmlspecialchars($receipt->dest_name) ?></p>
            
            <hr style="margin: 1.5rem 0; border: none; border-top: 1px solid var(--gray-200);">
            <h3 class="mb-3">Schedule & Logic</h3>
            <div class="grid grid-cols-2">
                <p><strong>Booking Date:</strong> <br> <?= date('d M Y - H:i', strtotime($receipt->booking_date)) ?></p>
                <p><strong>Trip Start Logic:</strong> <br> <?= htmlspecialchars($receipt->trip_start_mode) ?></p>
                <p><strong>Departure Date:</strong> <br> <?= date('d M Y', strtotime($receipt->start_date)) ?></p>
                <p><strong>Return Date:</strong> <br> <?= date('d M Y', strtotime($receipt->end_date)) ?></p>
                <p><strong>Total Duration:</strong> <br> <?= $receipt->duration ?> Days</p>
                <p><strong>Transport:</strong> <br> <?= htmlspecialchars($receipt->transport_mode) ?></p>
            </div>
            
            <hr style="margin: 1.5rem 0; border: none; border-top: 1px solid var(--gray-200);">
            <h3 class="mb-3">Assigned Guide Information</h3>
            <?php if($receipt->guide_name): ?>
                <div style="background: var(--light); padding: 15px; border-radius: 8px;">
                    <p>👨‍✈️ <strong>Guide:</strong> <?= htmlspecialchars($receipt->guide_name) ?></p>
                    <p>📞 <strong>Contact:</strong> <?= htmlspecialchars($receipt->guide_phone) ?></p>
                    <p class="text-gray-500" style="font-size: 0.875rem;">Your guide will contact you 24 hours before your travel date.</p>
                </div>
            <?php else: ?>
                <p class="text-gray-500">No guide has been assigned yet. Our admin will update this shortly.</p>
            <?php endif; ?>
        </div>

        <div class="glass-panel" style="position: sticky; top: 100px;">
            <h3 class="mb-3">Payment Outline</h3>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; color: var(--gray-500);">
                <span>Package Base</span>
                <span>₹<?= number_format($receipt->package_cost) ?></span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; color: var(--gray-500);">
                <span>Transport Fees</span>
                <span>₹<?= number_format($receipt->transport_cost) ?></span>
            </div>
            
            <hr style="margin: 1rem 0; border: none; border-top: 1px dashed var(--gray-200);">
            
            <div style="display: flex; justify-content: space-between; font-size: 1.25rem; font-weight: bold; margin-bottom: 1rem;">
                <span>Total Paid</span>
                <span style="color: var(--primary);">₹<?= number_format($receipt->total_cost) ?></span>
            </div>
            
            <p style="font-size: 0.8rem; text-align: right; color: var(--gray-500);">Txn ID: <?= $receipt->transaction_id ?></p>
            
            <div class="mt-4">
                <a href="itinerary.php?booking_id=<?= $receipt->id ?>" class="btn btn-primary" style="display: block; width: 100%;">View Visual Itinerary plan</a>
                <button onclick="window.print()" class="btn btn-secondary mt-2" style="display: block; width: 100%;">Print Document</button>
            </div>
        </div>
    </div>
</div>

<?php require_once 'includes/footer.php'; ?>
