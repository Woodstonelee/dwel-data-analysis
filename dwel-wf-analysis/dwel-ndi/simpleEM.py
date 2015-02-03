import numpy as np
from scipy.stats import norm

def fit_two_peaks_EM(sample, sigma, weights=False,
                     p0=np.array([0.1,0.2,0.6,0.2,0.5]),
                     max_iter=300, tolerance=1e-3):

    if not weights: w = np.ones(sample.size)
    else: w = 1./(sigma**2)
    w *= 1.*w.size/w.sum() # renormalization so they sum to N

    # Initial guess of parameters and initializations
    mu = np.array([p0[0], p0[2]])
    sig = np.array([p0[1], p0[3]])
    pi_ = np.array([p0[4], 1-p0[4]])

    gamma, N_ = np.zeros((2, sample.size)), np.zeros(2)
    p_new = np.array(p0)
    N = sample.size

    # EM loop
    counter = 0
    converged, stop_iteration = False, False
    while not stop_iteration:
        p_old = p_new
        # Compute the responsibility func. and new parameters
        for k in [0,1]:
            gamma[k,:] = w*pi_[k]*norm.pdf(sample, mu[k],
    sig[k])/pdf_model(sample, p_new) # SCHEME1
            #gamma[k,:] = pi_[k]*normpdf(sample, mu[k],
            #sig[k])/pdf_model(sample, p_new) # SCHEME2
            N_[k] = gamma[k,:].sum()
            mu[k] = np.sum(gamma[k]*sample)/N_[k] # SCHEME1
            #mu[k] = sum(w*gamma[k]*sample)/sum(w*gamma[k]) # SCHEME2
            sig[k] = np.sqrt( sum(gamma[k]*(sample-mu[k])**2)/N_[k] )
            pi_[k] = 1.*N_[k]/N
        p_new = np.array([mu[0], sig[0], mu[1], sig[1], pi_[0]])
#        import pdb; pdb.set_trace()
        assert np.abs(N_.sum() - N)/np.float_(N) < 1e-6
        assert np.abs(pi_.sum() - 1) < 1e-6

        # Convergence check
        counter += 1
        max_variation = max((p_new-p_old)/p_old)
        converged = True if max_variation < tolerance else False
        stop_iteration = converged or (counter >= max_iter)
    #print "Iterations:", counter
    if not converged: print "WARNING: Not converged"
    return p_new

def pdf_model(x, p):
    mu1, sig1, mu2, sig2, pi_1 = p
    return pi_1*norm.pdf(x, mu1, sig1) + (1-pi_1)*norm.pdf(x, mu2, sig2)
