"""
An example module with some sorting algorithms and some benchmarking code.

Sorting code algorithms from https://realpython.com/sorting-algorithms-python
"""

import random
import timeit
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import partial
from random import randint

from loguru import logger


class SortingAlgo(ABC):
    """A base class for sorting algorithms."""

    @abstractmethod
    def __call__(self, array: list) -> list:
        """Do the actual sorting."""


class BubbleSort(SortingAlgo):
    """A basic bubble sort implementation."""

    def __call__(self, array: list) -> list:
        n = len(array)
        for i in range(n):
            already_sorted = True
            for j in range(n - i - 1):
                if array[j] > array[j + 1]:
                    array[j], array[j + 1] = array[j + 1], array[j]
                    already_sorted = False
            if already_sorted:
                break
        return array


class InsertionSort(SortingAlgo):
    """A basic insertion sort implementation."""

    def __call__(self, array: list) -> list:
        for i in range(1, len(array)):
            key_item = array[i]
            j = i - 1
            while j >= 0 and array[j] > key_item:
                array[j + 1] = array[j]
                j -= 1
            array[j + 1] = key_item
        return array


class MergeSort(SortingAlgo):
    """A basic merge sort implementation."""

    @staticmethod
    def merge(left: list, right: list) -> list:
        """Perform a merge step."""
        if len(left) == 0:
            return right
        if len(right) == 0:
            return left

        result: list = []
        index_left = index_right = 0
        while len(result) < len(left) + len(right):
            if left[index_left] <= right[index_right]:
                result.append(left[index_left])
                index_left += 1
            else:
                result.append(right[index_right])
                index_right += 1
            if index_right == len(right):
                result += left[index_left:]
                break
            if index_left == len(left):
                result += right[index_right:]
                break
        return result

    def __call__(self, array: list) -> list:
        if len(array) < 2:
            return array
        midpoint = len(array) // 2
        return self.merge(left=self(array[:midpoint]), right=self(array[midpoint:]))


class QuickSort(SortingAlgo):
    """A basic quicksort implemenation."""

    def __call__(self, array: list) -> list:
        if len(array) < 2:
            return array
        low, same, high = [], [], []
        pivot = array[randint(0, len(array) - 1)]  # noqa: S311
        for item in array:
            if item < pivot:
                low.append(item)
            elif item == pivot:
                same.append(item)
            elif item > pivot:
                high.append(item)
        return self(low) + same + self(high)


@dataclass
class SortingBenchmark:
    sort_algos: list[SortingAlgo]
    num_runs: int = 10
    array_size: int = 100
    seed: int = 0

    def run(self) -> None:
        """Create random array, run sorting algorithms on it, and benchmark results."""

        array = [random.randint(0, self.array_size) for _ in range(self.array_size)]  # noqa: S311
        for sort_algo in self.sort_algos:
            time = timeit.timeit(partial(lambda algo=sort_algo: algo(array)), number=self.num_runs)
            logger.info(f"{type(sort_algo).__name__} time: {time} sec")
