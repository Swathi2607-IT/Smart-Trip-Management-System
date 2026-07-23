<?php
require_once 'header.php';

// Generate Statistics Summary
$userCount = $pdo->query("SELECT COUNT(*) FROM users")->fetchColumn();
$destCount = $pdo->query("SELECT COUNT(*) FROM destinations")->fetchColumn();
$bookingCount = $pdo->query("SELECT COUNT(*) FROM bookings WHERE status = 'Confirmed'")->fetchColumn();
$totalRevenue = $pdo->query("SELECT SUM(total_cost) FROM bookings WHERE status = 'Confirmed'")->fetchColumn();
?>

<div class="container section">
    <h1 class="mb-4">Admin Dashboard</h1>

    <div class="grid grid-cols-4 mb-4">
        <div class="glass-panel text-center" style="border-left: 4px solid var(--primary);">
            <h3 class="text-gray-500 mb-1">Total Users</h3>
            <p style="font-size: 2.5rem; font-weight: bold; color: var(--dark);"><?= $userCount ?></p>
        </div>
        <div class="glass-panel text-center" style="border-left: 4px solid var(--secondary);">
            <h3 class="text-gray-500 mb-1">Active Dest.</h3>
            <p style="font-size: 2.5rem; font-weight: bold; color: var(--dark);"><?= $destCount ?></p>
        </div>
        <div class="glass-panel text-center" style="border-left: 4px solid var(--warning);">
            <h3 class="text-gray-500 mb-1">Confirmed Trips</h3>
            <p style="font-size: 2.5rem; font-weight: bold; color: var(--dark);"><?= $bookingCount ?></p>
        </div>
        <div class="glass-panel text-center" style="border-left: 4px solid #10b981;">
            <h3 class="text-gray-500 mb-1">Total Revenue</h3>
            <p style="font-size: 2.5rem; font-weight: bold; color: var(--dark);">₹<?= number_format($totalRevenue) ?></p>
        </div>
    </div>

    <div class="glass-panel">
        <h2 class="mb-3">Recent Booking Activities</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="text-align: left; background: var(--gray-100); border-bottom: 2px solid var(--gray-200);">
                    <th style="padding: 10px;">ID</th>
                    <th style="padding: 10px;">User</th>
                    <th style="padding: 10px;">Destination</th>
                    <th style="padding: 10px;">Start Date</th>
                    <th style="padding: 10px;">Status</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $stmt = $pdo->query("
                    SELECT b.*, u.email as user_email, d.name as dest_name 
                    FROM bookings b 
                    JOIN users u ON b.user_id = u.id 
                    JOIN destinations d ON b.destination_id = d.id 
                    ORDER BY b.id DESC LIMIT 5
                ");
                while($row = $stmt->fetch()):
                ?>
                <tr style="border-bottom: 1px solid var(--gray-200);">
                    <td style="padding: 10px;">#<?= $row->id ?></td>
                    <td style="padding: 10px;"><?= htmlspecialchars($row->user_email) ?></td>
                    <td style="padding: 10px;"><?= htmlspecialchars($row->dest_name) ?></td>
                    <td style="padding: 10px;"><?= date('d M Y', strtotime($row->start_date)) ?></td>
                    <td style="padding: 10px;"><span class="badge status-<?= strtolower($row->status) ?>"><?= $row->status ?></span></td>
                </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
        <div class="mt-4 text-right">
            <a href="manage_bookings.php" class="btn btn-secondary text-sm">View All Bookings & Management</a>
        </div>
    </div>
</div>

</main>
</body>
</html>
