from inspect import currentframe, getframeinfo
print(getframeinfo(currentframe()).lineno)
import pycuda.driver as drv
print(getframeinfo(currentframe()).lineno)
import pycuda.tools
print(getframeinfo(currentframe()).lineno)
#import pycuda.autoinit
print(getframeinfo(currentframe()).lineno)
from pycuda.compiler import SourceModule
print(getframeinfo(currentframe()).lineno)
import numpy as np
print(getframeinfo(currentframe()).lineno)
drv.init()
print(getframeinfo(currentframe()).lineno)
a = numpy.random.randn(400).astype(numpy.float32)
b = numpy.random.randn(400).astype(numpy.float32)
mod = SourceModule("""
__global__ void multiply_them(float *dest, float *a, float *b)
{
  const int i = threadIdx.x;
  dest[i] = a[i] * b[i];
}
""")

dest = numpy.zeros_like(a)
multiply_them(
        drv.Out(dest), drv.In(a), drv.In(b),
        block=(400,1,1))