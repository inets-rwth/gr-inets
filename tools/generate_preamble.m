hpn = comm.PNSequence('Polynomial',[8 7 2 1 0], 'InitialConditions',[1 1 1 1 1 1 1 1 ], 'SamplesPerFrame', 128);
preamble = step(hpn);

figure;
c = xcorr(preamble,preamble);
plot(c);

preamble_diff = [];

for ii = 1:length(preamble)
    if(ii == 1)
        preamble_diff(ii) = preamble(ii);
    else
        preamble_diff(ii) = preamble(ii) * preamble(ii-1);
    end
end

length(preamble_diff)

figure;
c = xcorr(preamble_diff, preamble_diff);
plot(c);

csvwrite('ml_preamble_128.txt', transpose(preamble));
csvwrite('diff_ml_preamble_128.txt', preamble_diff);