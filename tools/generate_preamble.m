hpn = comm.PNSequence('Polynomial',[8 7 2 1 0], 'InitialConditions',[1 1 1 1 1 1 1 1 ], 'SamplesPerFrame', 256);
preamble = step(hpn);

figure;
c = xcorr(preamble,preamble);
plot(c);

preamble_diff = [];

for ii = 1:length(preamble)
    if(ii == 1)
        val = (preamble(ii)-0.5)*2;
        preamble_diff(ii) = val;
    else
        val = (preamble(ii)-0.5)*2;
        val2 = (preamble(ii-1)-0.5)*2;
        preamble_diff(ii) = val * val2;
    end
end

length(preamble_diff)

figure;
c = xcorr(preamble_diff, preamble_diff);
plot(c);

csvwrite('ml_preamble_256.txt', transpose(preamble));
csvwrite('diff_ml_preamble_256.txt', preamble_diff);

mod = [];
index = 1;
for ii = 1:2:length(preamble_diff)
    val = preamble_diff(ii) + 2 * preamble_diff(ii+1);
    if(val == 0)
        mod(index) = 1+0i; 
    end
    
    if(val == 1)
        mod(index) = 0+1i;
    end
    
    if(val == 2)
        mod(index) = -1+0i;
    end
    
    if(val == 3)
        mod(index) = 0-1i;
    end 
    index = index + 1;
end

figure;
c = xcorr(mod, mod);
%plot(real(mod),imag(mod));
plot(abs(c));

