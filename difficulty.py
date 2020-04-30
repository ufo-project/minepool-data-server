#!/usr/bin/env python
# encoding: utf-8


class UfoDiff(object):
    @staticmethod
    def genesis_nbits():
        return 0x1e00ffff

    @staticmethod
    def nbits_to_target(nbits):
        nbits = nbits & 0xffffffff
        nSize = nbits >> 24
        nWord = nbits & 0x007fffff
        if nSize <= 3:
            nWord >>= 8 * (3 - nSize)
        else:
            nWord <<= 8 * (nSize - 3)
        return nWord

    @staticmethod
    def get_target_work(target):
        return 2 ** 256 / float(target)

    @staticmethod
    def get_target0_work():
        nbits_0 = UfoDiff.genesis_nbits()
        target_0 = UfoDiff.nbits_to_target(nbits_0)
        work_0 = UfoDiff.get_target_work(target_0)
        return work_0

    @staticmethod
    def get_nbits_diff(nbits):
        shift = (nbits >> 24) & 0xff
        diff = float(0xffff) / (nbits & 0xffffff)
        while shift < 30:
            diff *= 256.0
            shift = shift + 1
        while shift > 30:
            diff /= 256.0
            shift = shift - 1
        return diff

    @staticmethod
    def get_target_diff(target):
        nbits_0 = UfoDiff.genesis_nbits()
        target_0 = UfoDiff.nbits_to_target(nbits_0)
        return float(target_0) / target

    @staticmethod
    def get_diff_work(diff):
        work0 = UfoDiff.get_target0_work()
        return float(work0) * diff

    @staticmethod
    def get_hash_rate_by_work(work, secs, unit):
        hash_rate = work / secs
        if unit in ('k', 'K'):
            return hash_rate / 1000.0
        elif unit in ('m', 'M'):
            return hash_rate / 1000.0 / 1000.0
        elif unit in ('g', 'G'):
            return hash_rate / 1000.0 / 1000.0 / 1000.0
        else:
            return hash_rate

    @staticmethod
    def get_hash_rate_by_diff(diff, secs, unit):
        work = UfoDiff.get_diff_work(diff)
        return UfoDiff.get_hash_rate_by_work(work, secs, unit)

    @staticmethod
    def get_hash_rate_by_nbits(nbits, secs, unit):
        work = UfoDiff.get_target_work(UfoDiff.nbits_to_target(nbits))
        return UfoDiff.get_hash_rate_by_work(work, secs, unit)


if __name__ == "__main__":
    diff = 5310440.537
    print(UfoDiff.get_hash_rate_by_diff(diff, 60, 'G'))
    nbits = 0x1b0328c4
    print(UfoDiff.get_hash_rate_by_nbits(nbits, 60, 'G'))


