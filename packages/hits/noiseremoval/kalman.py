"""
 Kalman filter implementation in Python

 The Kalman filter is an algorithm for the prediction of the true state of a noisy system.
 It works through prediction and measurement cycles wherein the previous state of the 
 system is considered.

 The key equations for the Kalman filter are:
        
    -----SCALAR VERSION-----------
    
    time update---------------------------------------------------------->
    x = A * x + B * u

    P_pri = A * P_pos * A + Q
    --------------------------------------------------------------------->
    
    measurement update--------------------------------------------------->

    K =   P_pri
        (P_pri + R) 

    P_pos = (I - K) * P_pri

    x_pos = x_pri + K * (z - H * x_pri)
    --------------------------------------------------------------------->


    -----MATRIX VERSION-----------
    where @ is the matrix multiplication operator:

    time update---------------------------------------------------------->
    x = A @ x + B @ u

    P_pri = A @ P_pos @ A + Q
    --------------------------------------------------------------------->
    
    measurement update--------------------------------------------------->
    e_pri = x - x_pri

    e_pos = x - x_pos

    K is equal to P_pri @ H_T @ (H @ P_pri @ H_T + R) ^ (-1) 
    inverse matrices are often numerically unstable therefore
    formulate as Alpha K = Beta and solve algorithmically
    for K.
    
    Alpha = H @ P_pri @ H_T + R

    Beta = P_pri @ H_T

    P_pos = (I - K @ H) @ P_pri

    x_pos = x_pri + K @ (z - H @ x_pri)
    --------------------------------------------------------------------->

 It is implemented here as a class to accept measured data and apply the Kalman filter.
 This returns a generator allowing large datasets to be used without being committed to memory twice.
 
 Current implementation supports 1-dimensional data.

 References:
    kalmanfilter.net
    Welch G, Bishop G; An Introduction to the Kalman Filter; UNC; 1994.

 Toby James 2018
"""
try:
    import filters
except(ImportError):
    from hits.noiseremoval import filters

#TODO implement extended Kalman and use to identify decay pattern for hits (assume exponential?)
#TODO can you transform detected (and Kalman-cleaned?) hits into some sort of linear space to get actual decaying exponential coefficents using basic Kalman??
#                                       answer: maybe??
#TODO decide on appropriate starting values for q and r.
#TODO implement multiple dimensional Kalman.

class KalmanData(filters.FilterData):
    
#public methods--------------------------------------------------------------- 
    def tweak_q(self, q):
        """Change the variance of the noise on the measurable value."""
        self._q = q
        self.reset()

    def tweak_r(self, r):
        """Change the variance of the noise on the measured value."""
        self._r = r
        self.reset()
#-----------------------------------------------------------------------------

#private variables and methods------------------------------------------------
    _q = None
    _r = None

    @staticmethod
    def _kalman(data_array, r=_r, q=_q, samples=50):
        """
        Accepts:
            
            An array.

        Accepts any array of numerical, real values.

        Performs the Kalman filter algorithm on the calculated data.

        Is a generator rather than a function. self._kalman_data is the generator applied to self._data.

        This data is accessible by calling the class as self().

        Kwargs:
            
            r (float, default=1):
                The variance of the noise on the measured data. Changeable through self.tweak_r().
            
            q (float, default is calculated as the variance of the first samples=samples.):
                The variance of the noise on the measurable data. Changeable through self.tweak_q().

            samples: (float, default=50):
                The number of samples to be used to calculated the variance on the data.
        
        Yields:
            
            The next value as predicted by the Kalman filter algorithm.
        """
        x = data_array[0]
        p = x**2
        if q is None:
            q = KalmanData._var(data_array, samples)
        i = 0
        while True:
            p = p + q
            try:
                z = data_array[i]
            except(IndexError):
                break
            if r is None:
                r = 1
            K = p/(p+r)
            x = x + K * (z - x)
            p = (1-K)*p
            yield x
            i += 1

    #reassign _filter function to _kalman function
    _filter = _kalman
#-----------------------------------------------------------------------------
