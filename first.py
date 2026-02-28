import torch
import numpy as np
data=[[8,9],[10,12]]
x=torch.tensor(data)
print(x)
arr=np.array(data)
x_np=torch.from_numpy(arr)
print("x_np",x_np)

x_ones=torch.ones_like(x)
print(f"Ones Tensor: \n {x_ones} \n")
x_rand=torch.rand_like(x,dtype=torch.float)
print(f"Random Tensor: \n {x_rand} \n")

shape=(2,3,)
torch.rand(shape)

tensor = torch.ones(4, 4)
print(f"First row: {tensor[0]}")
print(f"First column: {tensor[:, 0]}")
print(f"Last column: {tensor[:, -1]}")
tensor[:,1] = 0
print(tensor)

# Operations on Tensors
y1=tensor@tensor.T
y2=tensor.matmul(tensor.T)
y3=torch.rand_like(y1)
torch.matmul(tensor, tensor.T, out=y3)
print("y1",y1)
print("y2",y2)
print("y3",y3)

z1=tensor*tensor
z2=tensor.mul(tensor)
z3=torch.rand_like(tensor)
torch.mul(tensor,tensor,out=z3)
print("z1",z1)
print("z2",z2)
print("z3",z3)

agg=tensor.sum()
print(agg)
agg_item=agg.item()
print(agg_item,type(agg_item))

t = torch.ones(5)
print(f"t: {t}")
n = t.numpy()
print(f"n: {n}")

t.add_(1)
print(f"t: {t}")
print(f"n: {n}")



#print(torch.__version__)
#print(torch.backends.mps.is_available())
