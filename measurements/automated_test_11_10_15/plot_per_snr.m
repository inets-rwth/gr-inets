LINE_WIDTH = 1.5;
FONT_SIZE = 9.5;
FONT_NAME = 'Helvetica';

qpsk_data = dlmread('per_stats_log_qpsk.csv', ',', 1, 0);
bpsk_data = dlmread('per_stats_log_bpsk.csv', ',', 1, 0);

h=figure;

plot(bpsk_data(:,2), bpsk_data(:,3), 'b-o', 'LineWidth', LINE_WIDTH);
hold on
plot(qpsk_data(:,2), qpsk_data(:,3), 'r-o', 'LineWidth', LINE_WIDTH);

current_axis = gca;

set(current_axis, 'FontSize', FONT_SIZE, 'FontName', 'Times New Roman');
set(current_axis, 'Color', 'white', 'Box', 'off', 'TickDir', 'out');

xlabel('SNR [dB]', 'Fontsize', FONT_SIZE, 'FontName', FONT_NAME);
ylabel('PER', 'Fontsize', FONT_SIZE, 'FontName', FONT_NAME);

grid on;

%axis(axis_limits);

legend('BPSK', 'QPSK'); 

set(h, 'Units', 'Inches');
pos = get(h, 'Position');
set(h, 'PaperPositionMode', 'Auto', 'PaperUnits', 'Inches', 'PaperSize', [pos(3), pos(4)]);
print(h, strcat('./','per_vs_snr.pdf'), '-dpdf', '-r0');
