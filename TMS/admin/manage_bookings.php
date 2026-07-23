<?php
require_once 'header.php';

// Handle Guide Assignment
if($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['assign_guide'])) {
    $booking_id = (int)$_POST['booking_id'];
    $guide_id = (int)$_POST['guide_id'];
    
    $uStmt = $pdo->prepare("UPDATE bookings SET guide_id = ? WHERE id = ?");
    $uStmt->execute([$guide_id, $booking_id]);
    $msg = "Guide successfully assigned to booking #$booking_id.";
}

// Fetch Bookings with User and Dest info
$bStmt = $pdo->query("
    SELECT b.*, u.name as user_name, u.email as user_email, d.name as dest_name, g.name as guide_name
    FROM bookings b
    JOIN users u ON b.user_id = u.id
    JOIN destinations d ON b.destination_id = d.id
    LEFT JOIN guides g ON b.guide_id = g.id
    ORDER BY b.id DESC
");
$bookings = $bStmt->fetchAll();

// Fetch all guides for the dropdown
$gStmt = $pdo->query("SELECT id, name FROM guides");
$guides = $gStmt->fetchAll();
?>

<div class="container section">
    
    <?php if(isset($msg)): ?>
        <div class="alert alert-success"><?= htmlspecialchars($msg) ?></div>
    <?php endif; ?>

    <h2 class="mb-4">Manage System Bookings</h2>
    
    <div class="glass-panel" style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; min-width: 800px;">
            <thead>
                <tr style="text-align: left; background: var(--gray-100); border-bottom: 2px solid var(--gray-200);">
                    <th style="padding: 12px;">ID</th>
                    <th style="padding: 12px;">Traveler</th>
                    <th style="padding: 12px;">Destination & Dates</th>
                    <th style="padding: 12px;">Status</th>
                    <th style="padding: 12px;">Assigned Guide</th>
                    <th style="padding: 12px;">Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach($bookings as $b): ?>
                <tr style="border-bottom: 1px solid var(--gray-200);">
                    <td style="padding: 12px;">#<?= $b->id ?></td>
                    <td style="padding: 12px;">
                        <strong><?= htmlspecialchars($b->user_name) ?></strong><br>
                        <span style="font-size: 0.8rem; color: var(--gray-500);"><?= htmlspecialchars($b->user_email) ?></span>
                    </td>
                    <td style="padding: 12px;">
                        <strong><?= htmlspecialchars($b->dest_name) ?></strong><br>
                        <span style="font-size: 0.8rem; color: var(--gray-500);"><?= date('d M Y', strtotime($b->start_date)) ?> to <?= date('d M Y', strtotime($b->end_date)) ?></span>
                    </td>
                    <td style="padding: 12px;">
                        <span class="badge status-<?= strtolower($b->status) ?>"><?= $b->status ?></span><br>
                        <span style="font-size: 0.85rem;">₹<?= number_format($b->total_cost) ?></span>
                    </td>
                    <td style="padding: 12px;">
                        <?php if($b->guide_name): ?>
                            👨‍✈️ <?= htmlspecialchars($b->guide_name) ?>
                        <?php else: ?>
                            <span class="text-gray-500">Unassigned</span>
                        <?php endif; ?>
                    </td>
                    <td style="padding: 12px;">
                        <?php if($b->status === 'Confirmed' || $b->status === 'Pending'): ?>
                        <form method="POST" action="manage_bookings.php" style="display: flex; gap: 5px;">
                            <input type="hidden" name="booking_id" value="<?= $b->id ?>">
                            <select name="guide_id" class="form-control" style="padding: 5px; font-size: 0.8rem; width: 120px;" required>
                                <option value="">Select Guide...</option>
                                <?php foreach($guides as $g): ?>
                                    <option value="<?= $g->id ?>"><?= htmlspecialchars($g->name) ?></option>
                                <?php endforeach; ?>
                            </select>
                            <button type="submit" name="assign_guide" class="btn btn-primary" style="padding: 5px 10px; font-size: 0.8rem;">Assign</button>
                        </form>
                        <?php else: ?>
                        <span style="font-size: 0.9rem; color: var(--gray-500);">N/A (Cancelled)</span>
                        <?php endif; ?>
                    </td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>

</div>

</main>
</body>
</html>
